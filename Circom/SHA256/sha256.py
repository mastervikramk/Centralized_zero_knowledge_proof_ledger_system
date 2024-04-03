import hashlib
import json
import struct

class HashGenerator:
    @staticmethod
    def bits(bytestr):
        return ''.join(format(byte, '08b') for byte in bytestr)

    @staticmethod
    def count_bits(component):
        if isinstance(component, int):
            return len(HashGenerator.bits(struct.pack('>Q', component)))
        elif isinstance(component, str):
            return len(HashGenerator.bits(component.encode()))
        else:
            raise ValueError("Unsupported type for component")

    @staticmethod
    def sha256_hash(*components):
        concatenated_input = b''
        for component in components:
            if isinstance(component, int):
                concatenated_input += struct.pack('>Q', component)
            elif isinstance(component, str):
                concatenated_input += component.encode()
            else:
                raise ValueError("Unsupported type for component")
        
        sha256 = hashlib.sha256(concatenated_input)
        return sha256.digest()

    def generate_hash(self, *components):
        output = HashGenerator.sha256_hash(*components)
        io = {}
        for idx, component in enumerate(components):
            if isinstance(component, int):
                bit_array = [int(bit) for bit in HashGenerator.bits(struct.pack('>Q', component))]
            elif isinstance(component, str):
                bit_array = [int(bit) for bit in HashGenerator.bits(component.encode())]
            else:
                raise ValueError("Unsupported type for component")
            io[f"component_{idx}"] = bit_array
        
        io["hash"] = [int(bit) for bit in HashGenerator.bits(output)]
        return json.dumps(io)

if __name__ == "__main__":
    hash_generator = HashGenerator()
    utxo_id = 1
    output_address = '2Y1aAMVLzhoeBvEm6antX1EbP5PR'
    amount = 30
    signature = '5b270a90f3404d53d00541dee19ec8348f212e9fc2a15e448acaa435b05a6b4a8a4ca9131333f0932fdde0a4589e9d75'
    
    hash_result = hash_generator.generate_hash(utxo_id, output_address, amount, signature)
    print(hash_result)

    # Print counts
    for idx, component in enumerate([utxo_id, output_address, amount, signature]):
        print(f"Component {idx} bit count: {HashGenerator.count_bits(component)}")
