import pytest
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from keys import KeyPair

@pytest.fixture
def keypair():
    return KeyPair()

def test_create(keypair):
    assert keypair.private_key is not None
    assert keypair.public_key is not None

def test_create_address(keypair):
    address = keypair.create_address() 
    assert isinstance(address, str)

def test_private_key_to_mnemonic(keypair):
    mnemonic = keypair.private_key_to_mnemonic()
    assert isinstance(mnemonic, str)

@pytest.fixture
def mnemonic(keypair):
    return keypair.private_key_to_mnemonic()

def test_mnemonic_to_private_key(mnemonic, keypair):
    private_key = KeyPair.mnemonic_to_private_key(mnemonic)
    assert private_key.to_string() == keypair.private_key.to_string()
