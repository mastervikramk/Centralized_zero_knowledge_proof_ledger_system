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
    def sha256_hash(utxo_id, output_address, num):
        concatenated_input = HashGenerator.int_to_byte(utxo_id) + output_address.encode() + HashGenerator.int_to_byte(num)
        sha256 = hashlib.sha256(concatenated_input)
        print(f"input={HashGenerator.bits(concatenated_input)}")
        print(f'sha hex={sha256.hexdigest()}')
        print(f'sha bin={HashGenerator.bits(sha256.digest())}')
        print(f'sha bin reverse={HashGenerator.bits(sha256.digest())[::-1]}')
        return sha256.digest()

    @staticmethod
    def int_to_byte(num):
        assert 0 <= num < 256
        return num.to_bytes(1, byteorder='big', signed=False)

    def generate_hash(self, utxo_id, output_address, amount):
        output = HashGenerator.sha256_hash(utxo_id, output_address, amount)
        io = {
            "utxo_id": HashGenerator.bitarray(HashGenerator.int_to_byte(utxo_id)),
            "output_address": HashGenerator.bitarray(output_address.encode()),
            "amount": HashGenerator.bitarray(HashGenerator.int_to_byte(amount)),
            "hash": HashGenerator.bitarray(output)
        }
        return json.dumps(io)


if __name__ == "__main__":
    hash_generator = HashGenerator()
    utxo_id = 1
    output_address = '2Y1aAMVLzhoeBvEm6antX1EbP5PR'
    amount = 30
    print(hash_generator.generate_hash(utxo_id, output_address, amount))
