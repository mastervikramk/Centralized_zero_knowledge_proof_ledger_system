
import ecdsa
from mnemonic import Mnemonic
import hashlib
import base58

class KeyPair:
    #Generating private and public keys
    @staticmethod
    def generate_crypto_key_pair():
        private_key = ecdsa.SigningKey.generate()
        public_key = private_key.get_verifying_key()
        return private_key, public_key
    
    #Generating BIP-39 mnemonic of 18 words from private key (hex)
    @staticmethod
    def private_key_to_mnemonic(private_key):
        private_key_bytes = bytes.fromhex(private_key)
        return Mnemonic("english").to_mnemonic(private_key_bytes)
 
    #Converting mnemonic back to private key (hex)
    @staticmethod
    def mnemonic_to_private_key(mnemonic):
        entropy = Mnemonic("english").to_entropy(mnemonic)
        return entropy.hex()
    
    #Generating address
    @staticmethod
    def generate_crypto_address(public_key):
        public_key_bytes = public_key.to_string()
        sha256_hash = hashlib.sha256(public_key_bytes).digest()#sha256 hashing
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()#ripemd160 hashing
        address = base58.b58encode(ripemd160_hash)#base58 encoding
        return address.decode('utf-8')
