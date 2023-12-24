from bitcoinlib.blocks import Block

def parse_first_block(blk_file_path):
    try:
        with open(blk_file_path, 'rb') as file:
            # Read the first block from the file
            first_block = Block.parse(file)

            # Print block details
            print("Version:", int.from_bytes(first_block.version, byteorder='little'))
            print("Previous Block Hash:", first_block.prev_block.hex())
            print("Merkle Root:", first_block.merkle_root.hex())
            print("Timestamp:", first_block.time)
            print("Bits:", first_block.bits)
            print("Nonce:", first_block.nonce)

            # Print transaction details
            for i, tx in enumerate(first_block.transactions):
                print(f"\nTransaction {i + 1}:")
                print("Version:", tx.version)
                print("Lock Time:", tx.lock_time)

                # Print inputs
                print("\nInputs:")
                for j, tx_input in enumerate(tx.tx_inputs):
                    print(f"Input {j + 1}:")
                    print("   Previous Output Hash:", tx_input.prevout.hash.hex())
                    print("   Previous Output Index:", tx_input.prevout.n)
                    print("   Script Size:", len(tx_input.script))
                    print("   Script Bytes:", tx_input.script.hex())
                    print("   Sequence:", tx_input.sequence)

                # Print outputs
                print("\nOutputs:")
                for k, tx_output in enumerate(tx.tx_outputs):
                    print(f"Output {k + 1}:")
                    print("   Value (Satoshis):", tx_output.value)
                    print("   Script Size:", len(tx_output.scriptPubKey))
                    print("   Script Bytes:", tx_output.scriptPubKey.hex())

    except FileNotFoundError:
        print(f"Error: File '{blk_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace 'path/to/your/blkfile.blk' with the path to your Bitcoin ".blk" file
    blk_file_path = '0lk'

    parse_first_block(blk_file_path)
