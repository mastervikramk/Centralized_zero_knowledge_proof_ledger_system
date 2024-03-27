# compute sha256 hash of the array of input ints
# assume each int fits in 64 bits

# Remember:
#   SHA takes n-bits as input
#   immediately adds a 1 bit to the end of the message
#   then pads it with 0s until the length of the message 
#   is congruent to 448 mod 512. And then puts the length
#   (i.e. n-bits) as a uint64 at the end of the message.
#
#   So, the sha256 of "1" and 0x1 and 0x0000000000000001
#   are very different from each other

import hashlib
import json


def bits(bytestr):
    return ''.join(format(byte, '08b') for byte in bytestr)


def bitarray(bytestr):
    return [int(b) for b in bits(bytestr)]


def sha256_hash(input):
    # input is a bytestr 
    # output is a sha256 digest (32 bytes)

    sha256 = hashlib.sha256(input)
    print(f"input={bits(input)}")
    print(f'sha hex={sha256.hexdigest()}')
    print(f'sha bin={bits(sha256.digest())}')
    print(f'sha bin reverse={bits(sha256.digest())[::-1]}')
    return sha256.digest()

def int_to_byte(num):
    assert 0 <= num < 256
    return num.to_bytes(1, byteorder='big', signed=False)


if __name__ == "__main__":
    input = int_to_byte(1)
    # input = b'Hi'  # Use SHA256Hasher(16) with this
    output = sha256_hash(input)
    io = {"inputs": bitarray(input), "hash": bitarray(output)}
    print(json.dumps(io))
