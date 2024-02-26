import pytest
import os
import sys
from pytest_mock import mocker
from sqlalchemy.ext.declarative import declarative_base
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codes.models import Wallet, Utxo, Transaction

# Define the base class for declarative class definitions
Base = declarative_base()

def test_create_wallet(mocker):
    # Mock the session object
    mock_session = mocker.patch('codes.models.session')

    # Test creating a wallet
    address = "test_address"
    wallet = Wallet(address)
    mock_session.add.assert_called_once_with(wallet)
    mock_session.commit.assert_called_once()

def test_fetch_wallet_by_address(mocker):
    # Mock the session object
    mock_session = mocker.patch('codes.models.session')

    # Test fetching a wallet by address
    address = "test_address"
    wallet = Wallet(address)
    mock_session.query().filter_by().first.return_value = wallet

    fetched_wallet = Wallet.fetch_wallet_by_address(address)
    assert fetched_wallet == wallet

def test_create_utxo(mocker):
    # Mock the session object
    mock_session = mocker.patch('codes.models.session')

    # Create a Utxo
    utxo = Utxo.create_utxo(wallet_id=1, transaction_id=1, amount=10.0)
    # Assert that add and commit were called on the mock session
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_fetch_utxos_by_wallet(mocker):
    # Mock the session object
    mock_session = mocker.patch('codes.models.session')

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

def test_create_transaction(mocker):
    # Mock the session object
    mock_session = mocker.patch('codes.models.session')

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
    mock_session = mocker.patch('codes.models.session')

    # Test the is_valid_wallet_address method with a valid address
    mock_session.query().filter_by().count.return_value = 1  # Simulate a valid wallet address
    valid = Transaction.is_valid_wallet_address("test_address")
    assert valid == True

    # Test the is_valid_wallet_address method with an invalid address
    mock_session.query().filter_by().count.return_value = 0  # Simulate an invalid wallet address
    valid = Transaction.is_valid_wallet_address("invalid_address")
    assert valid == False
