import pytest
import os
import sys
from pytest_mock import mocker
from sqlalchemy.orm import declarative_base
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Wallet, Utxo, Transaction
from ecdsa import SigningKey, SECP256k1

# Define the base class for declarative class definitions
Base = declarative_base()

      #TEST CODES FOR WALLET CLASS

def test_create_wallet(mocker):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Test creating a wallet
    address = "test_address"
    wallet = Wallet(address)
    mock_session.add.assert_called_once_with(wallet)
    mock_session.commit.assert_called_once()

def test_fetch_wallet_by_address(mocker):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Test fetching a wallet by address
    address = "test_address"
    wallet = Wallet(address)
    #when query().filter_by().first() is called on the mocked session object, it returns the wallet object, simulating a database query that would return this wallet object.
    mock_session.query().filter_by().first.return_value = wallet

    fetched_wallet = Wallet.fetch_wallet_by_address(address)
    assert fetched_wallet == wallet



     #TEST CODES FOR UTXO CLASS

def test_create_utxo(mocker):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Create a Utxo
    utxo = Utxo.create_utxo(wallet_id=1, transaction_id=1, amount=10.0)
    # Assert that add and commit were called on the mock session
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_fetch_utxos_by_wallet(mocker):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Create some Utxos for a wallet
    utxo1 = Utxo.create_utxo(wallet_id=1, transaction_id=1, amount=5.0)
    utxo2 = Utxo.create_utxo(wallet_id=1, transaction_id=2, amount=8.0)

    # Mock the behavior of the session's query method to return the created Utxos
    mock_session.query.return_value.filter.return_value.all.return_value = [utxo1, utxo2]

    # Fetch Utxos by wallet ID
    utxos = Utxo.fetch_utxos_by_wallet(wallet_id=1)

    # Check that the correct number of Utxos are returned
    assert len(utxos) == 2
    assert utxo1 in utxos
    assert utxo2 in utxos



    #TEST CODES FOR TRANSACTION CLASS

def test_create_transaction(mocker):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Mock the UTXO objects for the inputs
    utxo1 = mocker.MagicMock(id=1)
    utxo2 = mocker.MagicMock(id=2)
    utxo3 = mocker.MagicMock(id=3)
    
    # Simulate the behavior of Utxo.create_utxo to return these mock objects
    mock_session.query().get.side_effect = [utxo1, utxo2, utxo3]

    # Test creating a transaction with UTXO objects as inputs
    inputs = [utxo1, utxo2, utxo3]  # UTXO objects instead of IDs
    outputs = {"destination_address": "test_destination", "amount": 10.0}  # Example outputs
    signatures = ["signature1", "signature2"]  # Example signatures
    create_money = True  # Example value for create_money

    transaction = Transaction.create_transaction(inputs, outputs, signatures, create_money)
    
    # Assert that add and commit were called on the mock session
    mock_session.add.assert_called_once_with(transaction)
    mock_session.commit.assert_called_once()

def test_is_valid_wallet_address(mocker):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Test the is_valid_wallet_address method with a valid address
    mock_session.query().filter_by().count.return_value = 1  # Simulate a valid wallet address
    valid = Transaction.is_valid_wallet_address("test_address")
    assert valid == True

    # Test the is_valid_wallet_address method with an invalid address
    mock_session.query().filter_by().count.return_value = 0  # Simulate an invalid wallet address
    valid = Transaction.is_valid_wallet_address("invalid_address")
    assert valid == False


@pytest.mark.parametrize("authorized_address, destination_address, amount, expected_result, expected_error", [
    ("valid_address", "valid_destination", 10.0, True, None),  # Valid inputs
    # ("invalid_address", "valid_destination", 10.0, False, "Invalid authorized address: invalid_address"),  # Invalid authorized address
    # ("valid_address", "invalid_destination", 10.0, False, "Invalid destination address: invalid_destination"),  # Invalid destination address
    ("valid_address", "valid_destination", -5.0, False, "Invalid amount: -5.0"),  # Negative amount
    ("valid_address", "valid_destination", "invalid_amount", False, "Invalid amount: invalid_amount"),  # Invalid amount type
    ("valid_address", "valid_destination", 0, False, "Invalid amount: 0"),  # Amount is zero
   
])
def test_verify_create_money_inputs(mocker, authorized_address, destination_address, amount, expected_result, expected_error):
    # Mock the session object
    mock_session = mocker.patch('models.session')

    # Mock the behavior of fetch_wallet_by_address method
    mock_wallet = mocker.MagicMock()
    mock_wallet.authorize_address_to_create_money.return_value = (authorized_address == "valid_address")  # Simulate authorization behavior
    mock_session.query().filter_by().first.return_value = mock_wallet

    # Call the method to test
    result, error = Transaction.verify_create_money_inputs(authorized_address, destination_address, amount)

    # Assertions
    assert result == expected_result
    assert error == expected_error
  

def test_sign_transaction():
    # Generate a private key
    private_key = SigningKey.generate(curve=SECP256k1)
    # Generate some transaction data (e.g., bytes)
    transaction_data = b"example_transaction_data"
    # Sign the transaction
    signature = Transaction.sign_transaction(private_key, transaction_data)
    # Assert the signature is not empty
    assert signature

def test_verify_signature():
    # Generate a key pair
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key
    # Generate some transaction data (e.g., bytes)
    transaction_data = b"example_transaction_data"
    # Sign the transaction
    signature = private_key.sign(transaction_data)
    # Verify the signature
    assert Transaction.verify_signature(public_key, transaction_data, signature)


@pytest.mark.parametrize("source_addresses, transfer_details_list, expected_result, expected_error", [
    (["source_address_1", "source_address_2"], 
     [{"source_address": "source_address_1", "destination_address": "destination_address_1", "amount": 10.0},
      {"source_address": "source_address_2", "destination_address": "destination_address_2", "amount": 20.0}],
     True, None),  # Valid transfer details

    (["source_address_1", "source_address_2"], 
     [{"source_address": "invalid_source_address", "destination_address": "destination_address_1", "amount": 10.0}],
     False, "Invalid source address: invalid_source_address"),  # Invalid source address

    (["source_address_1", "source_address_2"], 
     [{"source_address": "source_address_1", "destination_address": "invalid_destination_address", "amount": 10.0}],
     False, "Invalid destination address: invalid_destination_address"),  # Invalid destination address

    # Add more test cases as needed
])
def test_validate_transfer(source_addresses, transfer_details_list, expected_result, expected_error, mocker):
    # Patching is_valid_wallet_address method
    mock_is_valid_address = mocker.patch.object(Transaction, 'is_valid_wallet_address')

    # For the invalid destination address, mock is_valid_wallet_address to return False
    invalid_destination_address = "invalid_destination_address"
    mock_is_valid_address.side_effect = lambda address: address != invalid_destination_address

    # Call the method to test
    result, error = Transaction.validate_transfer(source_addresses, transfer_details_list)

    # Assertions
    assert result == expected_result
    assert error == expected_error