import pytest
import os,sys
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codes.models import Wallet, Base

@pytest.fixture
def mock_session():
    # Mock the session object
    with patch('codes.models.session') as mock_session:
        yield mock_session

def test_create_wallet(mock_session):
    # Test creating a wallet
    address = "test_address"
    wallet = Wallet(address)
    mock_session.add.assert_called_once_with(wallet)
    mock_session.commit.assert_called_once()


def test_fetch_wallet_by_address(mock_session):
    # Test fetching a wallet by address
    address = "test_address"
    wallet = Wallet(address)
    mock_session.query().filter_by().first.return_value = wallet

    fetched_wallet = Wallet.fetch_wallet_by_address(address)
    assert fetched_wallet == wallet