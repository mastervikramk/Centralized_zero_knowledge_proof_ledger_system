import json

def read_varint(file):
    result = 0
    shift = 0
    while True:
        byte = file.read(1)
        if not byte:
            break
        result |= (byte[0] & 0x7F) << shift
        shift += 7
        if not byte[0] & 0x80:
            break
    return result

def read_byte_array(file, length):
    return file.read(length)

def read_transaction(file):
    version = int.from_bytes(file.read(4), byteorder='little')

    input_count = read_varint(file)
    inputs = []
    for _ in range(input_count):
        txn_hash = read_byte_array(file, 32)
        index = int.from_bytes(file.read(4), byteorder='little')
        script_size = read_varint(file)
        input_script = read_byte_array(file, script_size)
        sequence = int.from_bytes(file.read(4), byteorder='little')
        inputs.append({
            'txn_hash': txn_hash.hex(),
            'index': index,
            'input_script_size': script_size,
            'input_script_bytes': input_script.hex(),
            'sequence': sequence
        })

    output_count = read_varint(file)
    outputs = []
    for _ in range(output_count):
        satoshis = int.from_bytes(file.read(8), byteorder='little')
        script_size = read_varint(file)
        output_script = read_byte_array(file, script_size)
        outputs.append({
            'satoshis': satoshis,
            'output_script_size': script_size,
            'output_script_bytes': output_script.hex()
        })

    return {
        'version': version,
        'txn_inputs': inputs,
        'txn_outputs': outputs
    }

def read_first_block_and_return_dict(blk_file_path, json_file_path):
    try:
        with open(blk_file_path, 'rb') as file:
            # Read the first block from the file
            version = int.from_bytes(file.read(4), byteorder='little')
            previous_block_hash = read_byte_array(file, 32)
            merkle_root = read_byte_array(file, 32)
            time = int.from_bytes(file.read(4), byteorder='little')
            bits = read_byte_array(file, 4)
            nonce = int.from_bytes(file.read(4), byteorder='little')

            transactions = []
            txn_count = read_varint(file)

            for _ in range(txn_count):
                transaction = read_transaction(file)
                if not transactions or transactions[-1] != transaction:
                    transactions.append(transaction)

            first_block_dict = {
                'version': version,
                'previous_block_hash': previous_block_hash.hex(),
                'merkle_root': merkle_root.hex(),
                'time': time,
                'bits': bits.hex(),
                'nonce': nonce,
                'txn_count': txn_count,
                'transactions': transactions
            }

            # Save the output in a JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(first_block_dict, json_file, indent=2)

            print("Output saved to", json_file_path)
            return first_block_dict

    except FileNotFoundError:
        print(f"Error: File '{blk_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace 'path/to/your/blkfile.blk' with the path to your Bitcoin ".blk" file
    blk_file_path = '0.blk'
    json_file_path = 'output.json'

    read_first_block_and_return_dict(blk_file_path, json_file_path)
