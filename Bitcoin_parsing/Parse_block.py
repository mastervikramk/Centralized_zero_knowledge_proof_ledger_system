import struct
import json
from datetime import datetime, timezone
import io

def parse_varint(file):
    value = 0
    shift = 0
    size = 0  # Initialize size to 0
    while True:
        byte = file.read(1)
        size += 1  # Increment size for each byte read
        if not byte:
            break
        value |= (byte[0] & 0x7F) << shift
        shift += 7
        if not byte[0] & 0x80:
            break
    return value, size

def parse_transaction(file):
    version = struct.unpack('>I', file.read(4))[0]  # Change byteorder to 'big'

    input_count, size = parse_varint(file)
    print("txn_in_count:", input_count)
    # print("Input_size:",size)
    inputs = []
    for _ in range(input_count):
        txn_hash = file.read(32)[::-1].hex()
        index = struct.unpack('>I', file.read(4))[0]  # Change byteorder to 'big'
        script_size, script_size_shift = parse_varint(file)
        input_script = file.read(script_size)
        sequence = struct.unpack('>I', file.read(4))[0]  # Change byteorder to 'big'
        inputs.append({
            'prev_tx_hash': txn_hash,
            'prev_output_index': index,
            'input_script_size': script_size,
            'input_script_bytes': input_script.hex(),
            'sequence': sequence
        })

    output_count, size = parse_varint(file)
    print("txn_out_count:", output_count)
    # print("output_size:",size)
    outputs = []
    for _ in range(output_count):
        satoshis = struct.unpack('<Q', file.read(8))[0]  # Keep byteorder as 'little'
        script_size, script_size_shift = parse_varint(file)
        output_script = file.read(script_size)
        outputs.append({
            'satoshis': satoshis,
            'output_script_size': script_size,
            'output_script_bytes': output_script.hex()
        })

    lock_time = struct.unpack('<I', file.read(4))[0]  # Keep byteorder as 'little'

    return {
        'version': version,
        'txn_inputs': inputs,
        'txn_outputs': outputs,
        'lock_time': lock_time
    }

def parse_block(file_path):
    with open(file_path, 'rb') as file:
        blocks = []
        for block_number in range(number_of_blocks_to_parse):  # Read only the first block
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

            try:
                timestamp, = struct.unpack('<I', block_data[68:72])
                timestamp_readable = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
            except ValueError:
                timestamp_readable = "Invalid Timestamp"

            bits, = struct.unpack('<I', block_data[72:76])
            nonce, = struct.unpack('<I', block_data[76:80])

            nbits = format(bits, '08x')

            block_header = {
                "version": version,
                "prev_block_hash": prev_block_hash,
                "merkle_root": merkle_root,
                "timestamp_readable": timestamp_readable,
                "nbits": nbits,
                "nonce": nonce,
                "block_number": block_number
            }

            # Parse transaction count (varint)
            tx_count, size = parse_varint(io.BytesIO(block_data[80:]))
            current_offset = 80 + size

            if 'tx_count' not in locals():
                print("Error: tx_count not defined.")
                return None

            # Parse transactions
            transactions = []
            for transaction_number in range(tx_count):
                tx_data = io.BytesIO(block_data[current_offset:])
                parsed_transaction = parse_transaction(tx_data)
                if parsed_transaction:
                    transactions.append(parsed_transaction)
                    current_offset += len(tx_data.getvalue())

            block = {
                "magic_number": magic.hex(),
                "block_size": block_size,
                "block_header": block_header,
                "transaction_count": tx_count,
                "transactions": transactions,
                "block_number": block_number,
                "txn_input_count": sum(len(tx['txn_inputs']) for tx in transactions),
                "txn_output_count": sum(len(tx['txn_outputs']) for tx in transactions)
            }

            blocks.append(block)

        return {"blocks": blocks}  # Include 'blocks' key at the top level

if __name__ == "__main__":
    # Replace 'path/to/your/blockfile.blk' with the path to your .blk file
    block_file_path = 'blk00000-b0.blk'
    output_json_file = 'blk00000-b0.blk.json'
    number_of_blocks_to_parse=1
    # Parse the first block
    parsed_blocks = parse_block(block_file_path)
    

    if parsed_blocks:
        # Save the output in a JSON file
        with open(output_json_file, 'w') as json_file:
            json.dump(parsed_blocks, json_file, indent=2)

        print("Output saved to", output_json_file)
