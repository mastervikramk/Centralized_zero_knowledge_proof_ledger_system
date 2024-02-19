from models import Wallet, Utxo, Transaction
from keys import KeyPair
import binascii

#CLASS TO CREATE MONEY, TRANSFER MONEY AND CHECK BALANCE
class Ledger:
    @classmethod
    def process_money_creation(cls, is_valid_signature, authorized_address, destination_address, amount, destination_wallet, signature):
        if destination_wallet and is_valid_signature:
            transaction = Transaction.create_transaction(
                inputs=[],
                outputs=[{'address': destination_address, 'amount': amount}],
                create_money=True,
                signatures=[signature.hex()]
            )
            # Creating utxos
            Utxo.create_utxo(destination_wallet.id, transaction.id, amount)

            print(f"Money created and transferred successfully from {authorized_address} to {destination_address}")
        else:
            print(f"Destination wallet not found: {destination_address}")
            
    @classmethod
    def process_transaction(cls, is_valid_signature, selected_utxos_ids, destination_address, transfer_amount,
                            total_selected_amount,source_address,source_wallet, signature):
        if is_valid_signature:
            signature_hex = binascii.hexlify(signature).decode()  # Convert signature bytes to hex string
            transaction = Transaction.create_transaction(
                inputs=selected_utxos_ids,
                outputs=[{'address': destination_address, 'amount': transfer_amount}],
                create_money=False,
                signatures=[signature_hex]  # Use the hex string representation of the signature
            )

            Utxo.create_utxo(
                Wallet.fetch_wallet_by_address(destination_address).id,
                transaction.id,
                transfer_amount
            )
        else:
            print("Not a valid signature")

        remaining_change = total_selected_amount - transfer_amount
        # Creating a new utxo in the source address after destroying the used ones
        if remaining_change > 0:
            change_utxo = Utxo.create_utxo(source_wallet.id, transaction.id, remaining_change)
            print(f"Change UTXO created: UTXO ID - {change_utxo.id}, Amount - {remaining_change}")

        print(f"Money transferred successfully from {source_address} to {destination_address}.")



class WalletManager:
    
    @classmethod
    def transfer_money(cls, source_addresses, transfer_details_list, public_keys):
        # Verifying the transfer details
        is_valid, error_message = Transaction.validate_transfer(source_addresses, transfer_details_list)

        if is_valid:
            for transfer_details, public_key in zip(transfer_details_list, public_keys):
                source_address = transfer_details.get('source_address')
                destination_address = transfer_details.get('destination_address')
                transfer_amount = transfer_details.get('amount', 0)

                source_wallet = Wallet.fetch_wallet_by_address(source_address)
                total_amount = Utxo.calculate_total_balance(
                    Utxo.fetch_available_utxos(source_wallet)
                )
                # Checking if the total amount in the source address is greater than the transfer amount
                if total_amount >= transfer_amount:
                    available_utxos = Utxo.fetch_available_utxos(source_wallet)
                    selected_utxos_ids, total_selected_amount = Utxo.show_utxos_and_select(
                        available_utxos, transfer_amount
                    )

                    transaction_data = {
                        "inputs": selected_utxos_ids,
                        "outputs": [{'address': destination_address, 'amount': transfer_amount}],
                        "create_money": False
                    }
                    transaction_data_bytes = str(transaction_data).encode('utf-8')
                    mnemonic_phrase = str(input("Enter the passphrase: "))

                    private_key = KeyPair.mnemonic_to_private_key(mnemonic_phrase)

                    # Signing the transaction data
                    signature = Transaction.sign_transaction(private_key, transaction_data_bytes)
                    # Verifying the signature
                    is_valid_signature = Transaction.verify_signature(public_key, transaction_data_bytes, signature)
                    # Creating a transaction and utxos
                    Ledger.process_transaction(is_valid_signature, selected_utxos_ids, destination_address,
                                             transfer_amount, total_selected_amount,source_address,source_wallet, signature)

                else:
                    print(f"Insufficient funds in {source_address}. Available balance: {total_amount}")
        else:
            print(f"Transfer validation failed: {error_message}")

    @classmethod
    def create_money(cls, authorized_address, destination_address, public_key, amount):
        # Verifying if the addresses are valid or not
        is_valid, error_message = Transaction.verify_create_money_inputs(
            authorized_address, destination_address, amount
        )

        if is_valid:
            destination_wallet = Wallet.fetch_wallet_by_address(destination_address)
            # Create a transaction_data dictionary
            transaction_data = {
                "inputs": [],
                "outputs": [{"address": destination_wallet, "amount": amount}],
                "create_money": True
            }
            transaction_data_bytes = str(transaction_data).encode('utf-8')
            mnemonic_phrase = str(input("Enter the passphrase: "))

            private_key = KeyPair.mnemonic_to_private_key(mnemonic_phrase)

            # Sign the transaction_data
            signature = Transaction.sign_transaction(private_key, transaction_data_bytes)
            # Verifying the signature
            is_valid_signature = Transaction.verify_signature(public_key, transaction_data_bytes, signature)

            # Call the process_money_creation function
            Ledger.process_money_creation(is_valid_signature, authorized_address, destination_address, amount, destination_wallet,
                                        signature)

        else:
            print(f"Create money validation failed: {error_message}")
        
    
    #Calculating the balance in an address
    @classmethod
    def balance(cls,address):
        wallet = Wallet.fetch_wallet_by_address(address)

        if wallet:
            available_utxos = Utxo.fetch_available_utxos(wallet)
            total_balance = Utxo.calculate_total_balance(available_utxos)
            return total_balance
        else:
            print(f"Wallet not found for address: {address}")
            return 0.0  # Assuming a default balance of 0 if the wallet is not found


