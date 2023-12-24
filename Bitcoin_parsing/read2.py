import json
import binascii
import io
from bitcoinlib.blocks import Block
from datetime import datetime

def convert_transaction_to_dict(transaction):
    return {
        'version': transaction.version,
        'txn_in_count': len(transaction.tx_inputs),
        'txn_inputs': [
            {
                'txn_hash': input.prevout.hash[::-1].hex(),  # Convert little-Endian to big-Endian
                'index': input.prevout.n,
                'input_script_size': len(input.script),
                'input_script_bytes': input.script.hex(),
                'sequence': input.sequence
            }
            for input in transaction.tx_inputs
        ],
        'txn_out_count': len(transaction.tx_outputs),
        'txn_outputs': [
            {
                'satoshis': output.value,
                'output_script_size': len(output.scriptPubKey),
                'output_script_bytes': output.scriptPubKey.hex()
            }
            for output in transaction.tx_outputs
        ],
        'lock_time': transaction.lock_time
    }

def convert_block_to_dict(block):
    return {
        'height': block.height,
        'file_position': 0,  # Assuming this is the start position in the file
        'version': int.from_bytes(block.version, byteorder='big'),  # Use big-endian
        'previous_hash': block.prev_block.hex()[::-1],  # Convert little-Endian to big-Endian
        'merkle_hash': block.merkle_root.hex()[::-1],  # Convert little-Endian to big-Endian
        'timestamp': block.time,
        'timestamp_readable': datetime.utcfromtimestamp(block.time).strftime('%Y-%m-%d %H:%M:%S'),
        'nbits': block.bits.hex(),
        'nonce': int.from_bytes(block.nonce, byteorder='big'),  # Use big-endian
        'txn_count': len(block.transactions),
        'transactions': [
            convert_transaction_to_dict(tx) for tx in block.transactions
        ]
    }

def read_hex_and_print_json(hex_file_path):
    try:
        with open(hex_file_path, 'r') as hex_file:
            hex_data = hex_file.read().strip()

            # Convert hex data to bytes
            block_data = binascii.unhexlify(hex_data)

            # Parse the block
            current_block = Block.parse(io.BytesIO(block_data))

            # Convert the block to a dictionary
            block_dict = {
                'blocks': [convert_block_to_dict(current_block)],
                'height': current_block.height
            }

            # Convert bytes to a serializable format
            def bytes_encoder(obj):
                if isinstance(obj, bytes):
                    try:
                        return obj.decode('utf-8')
                    except UnicodeDecodeError:
                        return obj.hex()
                raise TypeError

            # Print the JSON data
            print(json.dumps(block_dict, indent=2, default=bytes_encoder))

    except FileNotFoundError:
        print(f"Error: File '{hex_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace 'path/to/your/hex.txt' with the path to your hex file
    hex_file_path = 'hex.txt'

    read_hex_and_print_json(hex_file_path)
