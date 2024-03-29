import hashlib
import json


def bits(bytestr):
    return ''.join(format(byte, '08b') for byte in bytestr)


def bitarray(bytestr):
    return [int(b) for b in bits(bytestr)]


def sha256_hash(inputs):
    concatenated_input = b''.join(inputs)
    sha256 = hashlib.sha256(concatenated_input)
    print(f"input={bits(concatenated_input)}")
    print(f'sha hex={sha256.hexdigest()}')
    print(f'sha bin={bits(sha256.digest())}')
    print(f'sha bin reverse={bits(sha256.digest())[::-1]}')
    return sha256.digest()


def int_to_byte(num):
    assert 0 <= num < 256
    return num.to_bytes(1, byteorder='big', signed=False)


if __name__ == "__main__":
    inputs = [int_to_byte(1), b'2Y1aAMVLzhoeBvEm6antX1EbP5PR',int_to_byte(30)]  # Example inputs
    output = sha256_hash(inputs)
    io = {"inputs": [bitarray(inp) for inp in inputs], "hash": bitarray(output)}
    print(json.dumps(io))
