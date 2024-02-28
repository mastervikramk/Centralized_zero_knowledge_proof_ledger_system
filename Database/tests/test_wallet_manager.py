import pytest
from pytest_mock import mocker
from unittest.mock import patch, MagicMock
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wallet_manager import Ledger, WalletManager
from models import Wallet, Utxo, Transaction


class TestWalletManager:

    def test_balance_wallet_found(self, mocker):
        mock_wallet = MagicMock()
        mock_utxos = [MagicMock(amount=10.0), MagicMock(amount=5.0)]
        
        mocker.patch.object(Wallet, 'fetch_wallet_by_address', return_value=mock_wallet)
        mocker.patch.object(Utxo, 'fetch_available_utxos', return_value=mock_utxos)
        mocker.patch.object(Utxo, 'calculate_total_balance', return_value=15.0)
        
        assert WalletManager.balance('address') == 15.0

    def test_balance_wallet_not_found(self, mocker):
        mocker.patch.object(Wallet, 'fetch_wallet_by_address', return_value=None)
        
        assert WalletManager.balance('address') == 0.0
