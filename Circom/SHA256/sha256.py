import hashlib
import json


class HashGenerator:
    def __init__(self):
        pass

    @staticmethod
    def bits(bytestr):
        return ''.join(format(byte, '08b') for byte in bytestr)

    @staticmethod
    def bitarray(bytestr):
        return [int(b) for b in HashGenerator.bits(bytestr)]

    @staticmethod
    def sha256_hash(utxo_id, output_address, amount, signature):
        concatenated_input = HashGenerator.int_to_byte(utxo_id) + output_address.encode() + HashGenerator.int_to_byte(amount)+ signature.encode()
        sha256 = hashlib.sha256(concatenated_input)
        print(f"input={HashGenerator.bits(concatenated_input)}")
        print(f'sha hex={sha256.hexdigest()}')
        print(f'sha bin={HashGenerator.bits(sha256.digest())}')
        print(f'sha bin reverse={HashGenerator.bits(sha256.digest())[::-1]}')
        return sha256.digest()

    @staticmethod
    def int_to_byte(num, num_bytes=8):
        assert 0 <= num < 256 ** num_bytes
        return num.to_bytes(num_bytes, byteorder='big', signed=False)


    def generate_hash(self, utxo_id, output_address, amount,signature):
        output = HashGenerator.sha256_hash(utxo_id, output_address, amount,signature)
        io = {
            "utxo_id": HashGenerator.bitarray(HashGenerator.int_to_byte(utxo_id)),
            "output_address": HashGenerator.bitarray(output_address.encode()),
            "amount": HashGenerator.bitarray(HashGenerator.int_to_byte(amount)),
            "signature":HashGenerator.bitarray(signature.encode()),
            "hash": HashGenerator.bitarray(output)
        }
        return json.dumps(io)


if __name__ == "__main__":
    hash_generator = HashGenerator()
    utxo_id = 1
    output_address = '2Y1aAMVLzhoeBvEm6antX1EbP5PR'
    amount = 30
    signature='5b270a90f3404d53d00541dee19ec8348f212e9fc2a15e448acaa435b05a6b4a8a4ca9131333f0932fdde0a4589e9d75'
    print(hash_generator.generate_hash(utxo_id, output_address, amount,signature))
