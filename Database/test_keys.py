import pytest
from keys import KeyPair
import ecdsa
from mnemonic import Mnemonic
import hashlib
import base58

@pytest.fixture
def keypair():
    return KeyPair()

def test_create(keypair):
    assert keypair.private_key is not None
    assert keypair.public_key is not None

def test_create_method_calls_generate(keypair):
    keypair.create()
    assert keypair.private_key is not None
    assert keypair.public_key is not None

def test_private_key_to_mnemonic(keypair):
    mnemonic = keypair.private_key_to_mnemonic()
    assert isinstance(mnemonic, str)  # Check if mnemonic is a string

def test_create_address(keypair):
    address = keypair.create_address()
    assert isinstance(address, str)  # Check if address is a string

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
