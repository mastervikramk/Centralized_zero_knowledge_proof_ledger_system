import ecdsa
from mnemonic import Mnemonic
import hashlib
import base58

class KeyPair:
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    # Generating private and public keys
    def create(self):
        self.private_key = ecdsa.SigningKey.generate()
        self.public_key = self.private_key.get_verifying_key()
    
    # Generating BIP-39 mnemonic of 18 words from private key (hex)
    def private_key_to_mnemonic(self):
        private_key_bytes = self.private_key.to_string()
        return Mnemonic("english").to_mnemonic(private_key_bytes)
 
    # Generating address
    def create_address(self):
        public_key_bytes = self.public_key.to_string()
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        address = base58.b58encode(ripemd160_hash)
        return address.decode('utf-8')
    
    # Generating BIP-39 mnemonic from private key
    @staticmethod
    def mnemonic_to_private_key(mnemonic):
        entropy = Mnemonic("english").to_entropy(mnemonic)
        return entropy.hex()

