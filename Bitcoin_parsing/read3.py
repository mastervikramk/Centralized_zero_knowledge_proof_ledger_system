import json
from bitcoinlib.blocks import Block
from datetime import datetime

def convert_transaction_to_dict(transaction):
    return {
        'version': transaction.version,
        'txn_in_count': len(transaction.tx_inputs),
        'txn_inputs': [
            {
                'txn_hash': input.prevout.hash.hex(),
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
        'version': int.from_bytes(block.version, byteorder='little'),
        'previous_hash': block.prev_block.hex(),
        'merkle_hash': block.merkle_root.hex(),
        'timestamp': block.time,
        'timestamp_readable': datetime.utcfromtimestamp(block.time).strftime('%Y-%m-%d %H:%M:%S'),
        'nbits': block.bits.hex(),
        'nonce': block.nonce,
        'txn_count': len(block.transactions),
        'transactions': [
            convert_transaction_to_dict(tx) for tx in block.transactions
        ]
    }

def read_first_block_and_print_json(blk_file_path):
    try:
        with open(blk_file_path, 'rb') as file:
            # Read the first block from the file
            first_block = Block.parse(file)

            # Convert the first block to a dictionary
            first_block_dict = {
                'blocks': [convert_block_to_dict(first_block)],
                'height': 1  # Assuming height is 1 for the example
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
            print(json.dumps(first_block_dict, indent=2, default=bytes_encoder))

    except FileNotFoundError:
        print(f"Error: File '{blk_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace 'path/to/your/blkfile.blk' with the path to your Bitcoin ".blk" file
    blk_file_path = '0.blk'

    read_first_block_and_print_json(blk_file_path)
