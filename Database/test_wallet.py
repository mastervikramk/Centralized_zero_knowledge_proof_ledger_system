import os
import sys
import pytest
import ecdsa
from mnemonic import Mnemonic
import hashlib
import base58

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from source.wallet import WalletManager

def test_generate_crypto_key_pair():
    private_key,public_key= WalletManager.generate_crypto_key_pair()

    #check if the private key and public key are generated
    assert private_key is not None
    assert public_key is not None

#Signing transaction and verifying transaction is tested here
def test_signature():
    private_key,public_key=WalletManager.generate_crypto_key_pair()

    #message to sign
    transaction_data=b"hello1"
    
    #create different private key for the verification
    different_private_key=ecdsa.SigningKey.generate()

    #generate a signature using the private key
    signature=WalletManager.sign_transaction(different_private_key,transaction_data)

    actual_signature=WalletManager.sign_transaction(private_key,transaction_data)
    
    assert signature is not None
    assert actual_signature is not None

    assert signature != actual_signature
    #verify the signature using the pbulic key
    assert WalletManager.verify_signature(public_key,transaction_data,signature)==False
    # assert public_key.verify(actual_signature,transaction_data)==True
    assert WalletManager.verify_signature(public_key,transaction_data,actual_signature)==True

#private to mnemonic and vice-versa is tested here
def test_mnemonic():
    private_key=ecdsa.SigningKey.generate()
    private_key_hex=private_key.to_string().hex()
    private_key_bytes=bytes.fromhex(private_key_hex)

    print(private_key_hex)
    print(private_key_bytes)

    mnemo=Mnemonic("english")

    mnemonic=mnemo.to_mnemonic(private_key_bytes)

    # print("Mnemonic phrase:", mnemonic)
    entropy=mnemo.to_entropy(mnemonic)
    private_key_hex_new=entropy.hex()
    private_key_new = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex_new))
    # print(private_key_new)

    assert private_key_new.to_string()==private_key.to_string()
            

def test_generate_crypto_address():
    # Generate a public key
    private_key = ecdsa.SigningKey.generate()
    public_key = private_key.get_verifying_key()

    # Calculate the expected address using the same process
    public_key_bytes = public_key.to_string()
    sha256_hash = hashlib.sha256(public_key_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    expected_address = base58.b58encode(ripemd160_hash).decode('utf-8')

    # Call the method to generate the address
    generated_address = WalletManager.generate_crypto_address(public_key)

    # Check if the generated address matches the expected address
    assert generated_address == expected_address

