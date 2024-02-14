from models import Wallet, Utxo, Transaction
from keys import KeyPair
import ecdsa


#CLASS TO CREATE MONEY, TRANSFER MONEY AND CHECK BALANCE
class Ledger:
    @classmethod
    def create_money(cls, authorized_address, destination_address, public_key,amount):
        #Verifying if the addresses are valid or not
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
            transaction_data_bytes=str(transaction_data).encode('utf-8')
            mnemonic_phrase=str(input("Enter the passphrase: "))

            private_key_hex=KeyPair.mnemonic_to_private_key(mnemonic_phrase)
            
            private_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex))
            
            # Sign the transaction_data
            signature = Transaction.sign_transaction(private_key, transaction_data_bytes )
            #Verifying the signature
            is_valid_signature=Transaction.verify_signature(public_key,transaction_data_bytes,signature)


            #Creating transaction
            if destination_wallet and is_valid_signature:
                transaction = Transaction.create_transaction(
                    inputs=[],
                    outputs=[{'address': destination_address, 'amount': amount}],
                    create_money=True,
                    signatures=[signature.hex()]
                )
                #Creating utxos
                Utxo.create_utxo(destination_wallet.id, transaction.id, amount)

                print(f"Money created and transferred successfully from {authorized_address} to {destination_address}")
            else:
                print(f"Destination wallet not found: {destination_address}")
        else:
            print(f"Create money validation failed: {error_message}")
            

    #This code transfers the money from multiples source_addresses to multiple destination addresses
    @classmethod
    def transfer_money(cls, source_addresses, transfer_details_list, public_keys):
        #Verifying the transfer details
        is_valid, error_message = Transaction.validate_transfer(source_addresses, transfer_details_list)

        if is_valid:
            for transfer_details, public_key in zip(transfer_details_list,  public_keys):
                source_address = transfer_details.get('source_address')
                destination_address = transfer_details.get('destination_address')
                transfer_amount = transfer_details.get('amount', 0)

                source_wallet = Wallet.fetch_wallet_by_address(source_address)
                total_amount = Utxo.calculate_total_balance(
                    Utxo.fetch_available_utxos(source_wallet)
                )
                #checking if the total amount in source address is greater than the transfer amount
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
                    transaction_data_bytes=str(transaction_data).encode('utf-8')
                    mnemonic_phrase=str(input("Enter the passphrase: "))

                    private_key_hex=KeyPair.mnemonic_to_private_key(mnemonic_phrase)
                    
                    private_key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex))

                    #Signing the transaction  data
                    signature = Transaction.sign_transaction(private_key, transaction_data_bytes)
                    #Verifying the signature
                    is_valid_signature = Transaction.verify_signature(public_key, transaction_data_bytes, signature)
                    #Creating transaction and utxos
    
                    if is_valid_signature:
                        transaction = Transaction.create_transaction(
                            inputs=selected_utxos_ids,
                            outputs=[{'address': destination_address, 'amount': transfer_amount}],
                            create_money=False,
                            signatures=[signature.hex()]
                        )

                        Utxo.create_utxo(
                            Wallet.fetch_wallet_by_address(destination_address).id,
                            transaction.id,
                            transfer_amount
                        )
                    else:
                        print("Not valid signature")

                    remaining_change = total_selected_amount - transfer_amount
                    #Creating new utxo in the source address after destroying the used ones
                    if remaining_change > 0:
                        change_utxo = Utxo.create_utxo(source_wallet.id, transaction.id, remaining_change)
                        print(f"Change UTXO created: UTXO ID - {change_utxo.id}, Amount - {remaining_change}")

                    print(f"Money transferred successfully from {source_address} to {destination_address}.")
                else:
                    print(f"Insufficient funds in {source_address}. Available balance: {total_amount}")
        else:
            print(f"Transfer validation failed: {error_message}")
    
class WalletManager:
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


# Examples of using the WalletManager
keypair1= KeyPair()
keypair2= KeyPair()
keypair3= KeyPair()
keypair4= KeyPair()

keypair1.create()
keypair2.create()
keypair3.create()
keypair4.create()

private_key1, public_key1 = keypair1.private_key,keypair1.public_key
private_key2, public_key2 = keypair2.private_key,keypair2.public_key
private_key3, public_key3 = keypair3.private_key,keypair3.public_key
private_key4, public_key4 = keypair4.private_key,keypair4.public_key


private_key_hex4 = keypair4.private_key.to_string().hex()
mnemonic_phrase4 = keypair4.private_key_to_mnemonic()
print(mnemonic_phrase4)
recovered_private_key_hex4=KeyPair.mnemonic_to_private_key(mnemonic_phrase4)


private_key_hex1 = keypair1.private_key.to_string().hex()
mnemonic_phrase1 = keypair1.private_key_to_mnemonic()
print(mnemonic_phrase1)
recovered_private_key_hex1=KeyPair.mnemonic_to_private_key(mnemonic_phrase1)

address1=keypair1.create_address()
address2=keypair2.create_address()
address3=keypair3.create_address()
address4=keypair4.create_address()

Wallet.create_wallet(address=address1)
Wallet.create_wallet(address=address2) 
Wallet.create_wallet(address=address3)   
Wallet.create_wallet(address=address4)

Wallet.authorize_address_to_create_money(address=address4)


Ledger.create_money(authorized_address=address4, destination_address=address1, public_key=public_key4, amount=100.0)
# WalletManager.create_money(authorized_address=address4, destination_address=address2,private_key=private_key4,public_key=public_key4, amount=200.0)

transfer_details_list = [
    {'source_address': address1, 'destination_address': address3, 'amount': 30.0},
    # {'source_address': address2, 'destination_address': address3, 'amount': 40.0},
   
]

# # Private and public keys for multiple source addresses
# private_keys_list = [private_key1, private_key3]
public_keys_list = [public_key1]

Ledger.transfer_money(
    source_addresses=[address1, address2],
    transfer_details_list=transfer_details_list,
    public_keys=public_keys_list
)
balance = WalletManager.balance(address3)
print(f"Current balance of {address3}: {balance}")
