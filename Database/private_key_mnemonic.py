
from mnemonic import Mnemonic
import ecdsa

# Function to generate private and public key pair
def generate_crypto_key_pair():
    private_key = ecdsa.SigningKey.generate()  #private key
    public_key = private_key.get_verifying_key()  # Public key
    return private_key, public_key

# Initialize Mnemonic object with English wordlist
mnemo = Mnemonic("english")
# Generate BIP-39 mnemonic from private key

def private_key_to_mnemonic(private_key):
# Ensure the private key length is 64 characters (32 bytes)
    private_key_bytes = bytes.fromhex(private_key.zfill(64))
    return mnemo.to_mnemonic(private_key_bytes)


# Convert mnemonic back to private key
def mnemonic_to_private_key( mnemonic):
    entropy = mnemo.to_entropy(mnemonic)
    return entropy.hex().lstrip('0')[:64]  
#private key
private_key,public_key=generate_crypto_key_pair()

print(private_key)
#private hey hex
private_key_hex=private_key.to_string().hex()

print(private_key_hex)
#mnemonic_phrase
mnemonic_phrase =private_key_to_mnemonic(private_key_hex)

#recovered private key matches with private key hex
recovered_private_key_hex=mnemonic_to_private_key(mnemonic_phrase)
print(recovered_private_key_hex)
#recovered private_key
recovered_private_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex))
print(recovered_private_key)


#output
# <ecdsa.keys.SigningKey object at 0x000001E2BDC8ED10>
# f2f024a759d6974904481f1c76e4fe45d513b7ed1ab3fd22
# f2f024a759d6974904481f1c76e4fe45d513b7ed1ab3fd22
# <ecdsa.keys.SigningKey object at 0x000001E2BDD19CD0> 