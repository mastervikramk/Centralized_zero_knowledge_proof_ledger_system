import struct
import json
from datetime import datetime, timezone

def parse_varint(data):
    # Parse variable-length integers used in Bitcoin protocol
    value = 0
    shift = 0
    i = 0
    while True:
        byte = data[i]
        i += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            break
    return value, i

def parse_block(file_path):
    with open(file_path, 'rb') as file:
        # Read magic number
        magic = file.read(4)

        # Check if it's a valid Bitcoin block file
        if magic != b'\xf9\xbe\xb4\xd9':
            print("Invalid magic number. Not a Bitcoin block file.")
            return None

        # Read block size
        block_size = struct.unpack('<I', file.read(4))[0]

        # Read the entire block data
        block_data = file.read(block_size)

        # Parse the block header
        version, = struct.unpack('<I', block_data[:4])
        prev_block_hash = block_data[4:36][::-1].hex()
        merkle_root = block_data[36:68][::-1].hex()
        
        # Handle the case where timestamp is invalid
        try:
            timestamp, = struct.unpack('<I', block_data[68:72])
            timestamp_readable = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        except ValueError:
            timestamp_readable = "Invalid Timestamp"

        bits, = struct.unpack('<I', block_data[72:76])
        nonce, = struct.unpack('<I', block_data[76:80])

        # Convert bits to hexadecimal format
        nbits = format(bits, '08x')

        block_header = {
            "version": version,
            "prev_block_hash": prev_block_hash,
            "merkle_root": merkle_root,
            "timestamp_readable": timestamp_readable,
            "nbits": nbits,
            "nonce": nonce
        }

        # Parse transaction count (varint)
        tx_count, size = parse_varint(block_data[80:])
        current_offset = 80 + size

        # Parse transactions
        transactions = []
        for _ in range(tx_count):
            # Read transaction size
            tx_size = struct.unpack('<I', block_data[current_offset:current_offset + 4])[0]
            current_offset += 4

            # Read transaction data
            tx_data = block_data[current_offset:current_offset + tx_size]
            current_offset += tx_size

            # Append transaction data to the list
            transactions.append(tx_data.hex())

        block = {
            "magic_number": magic.hex(),
            "block_size": block_size,
            "block_header": block_header,
            "transaction_count": tx_count,
            "transactions": transactions
        }

        return block

def save_as_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=2)

if __name__ == "__main__":
    # Replace 'path/to/your/blockfile.blk' with the path to your .blk file
    block_file_path = '0.blk'
    output_json_file = 'parsed_block.json'  # Change the output file name as needed

    # Parse the block and save as JSON
    parsed_block = parse_block(block_file_path)
    if parsed_block:
        save_as_json(parsed_block, output_json_file)
        print(f"Block data saved to {output_json_file}")
