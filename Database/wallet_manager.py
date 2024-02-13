from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Wallet, Utxo, Transaction
from keys import KeyPair
import inquirer
import ecdsa
from keys import KeyPair

# Creating an SQLite database
engine = create_engine('sqlite:///wallet.db', echo=True)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


#CLASS TO DEAL WITH WALLET RELATED METHODS
class Wallet_new:
    @staticmethod
    def create_wallet(address):
        # Inserting a row into the "wallets" table
        wallet = Wallet(address=address)
        session.add(wallet)
        session.commit()
        print(f"Wallet inserted: Address - {address}")

    @staticmethod
    def authorize_address_to_create_money(address):
        # Authorize the wallet with the given address to create money
        wallet = Wallet_new.fetch_wallet_by_address(address)
        if wallet:
            wallet.authorize_address_to_create_money = True
            session.commit()
            print(f"Wallet {address} authorized to create money.")
        else:
            print(f"Wallet with the address {address} not found.")

    @staticmethod
    def fetch_wallet_by_address(address):
        # Fetch a wallet based on address
        return session.query(Wallet).filter_by(address=address).first()


#CLASS TO DEAL WITH UTXO RELATED METHODS
class Utxo_new:
    @staticmethod
    def create_utxo(wallet_id, transaction_id, amount):
        # Insert a row into the 'utxos' table
        utxo = Utxo(wallet_id=wallet_id, transaction_id=transaction_id, amount=amount)
        session.add(utxo)
        session.commit()
        print(f"UTXO inserted: Wallet ID - {wallet_id}, Amount - {amount}")
        return utxo
    
    @staticmethod
    def fetch_utxos_by_wallet(wallet_id):
        # Fetch UTXOs based on wallet ID
        return session.query(Utxo).filter(Utxo.wallet_id == wallet_id).all()
    
    @staticmethod
    def fetch_available_utxos(source_wallet):
        #Fetching all the utxos associated will the wallet
        source_utxos = Utxo_new.fetch_utxos_by_wallet(source_wallet.id)
        return [utxo for utxo in source_utxos if not Transaction_new.is_utxo_spent(utxo.id)]

    @staticmethod
    def calculate_total_balance(utxos):
        #Calculating total balance of all the utxos
        return sum(utxo.amount for utxo in utxos)
    
    #List which will keep the already selected/used utxos 
    used_utxos = []
    
    #The following method is for selecting the particular utxos for transaction
    @classmethod
    def show_utxos_and_select(cls, available_utxos, transfer_amount):
        # Not used utxos
        filtered_utxos = [utxo for utxo in available_utxos if utxo not in cls.used_utxos]
        
        #utxo information of the source address
        utxos_info = [
            (str(utxo.id), f"UTXO ID: {utxo.id}, Amount: {utxo.amount}")
            for utxo in filtered_utxos
        ]
        #total available amount to the source address
        total_available_amount = sum(utxo.amount for utxo in filtered_utxos)

        print(f"\nAmount to be transferred: {transfer_amount}")
        print(f"Total available amount in UTXOs: {total_available_amount}")
        print("\nAvailable UTXOs:")

        for utxo_info in utxos_info:
            print(utxo_info[1])  # Print UTXO information
        #Asks the user to select the utxos
        questions = [
            inquirer.Checkbox(
                'utxos',
                message="Select UTXOs to cover the transfer amount:",
                choices=utxos_info
            )
        ]

        answers = inquirer.prompt(questions)
        selected_utxos_ids = answers['utxos']

        # Store used UTXOs for persistence
        cls.used_utxos.extend(utxo for utxo in filtered_utxos if utxo.id in selected_utxos_ids)

        # Corrected line to create utxos_dict
        utxos_dict = {utxo_id: utxo for utxo_id, utxo in zip(selected_utxos_ids, filtered_utxos)}
        
        #utxos selected by the users to cover the transfer amount
        selected_utxos = [utxos_dict[utxo_id] for utxo_id in selected_utxos_ids]
        #total selected amount form the selected utxos
        total_selected_amount = sum(float(utxo.amount) for utxo in selected_utxos)
        
        return selected_utxos, total_selected_amount


#CLASS TO DEAL WITH TRANSACTION AND IT'S CONSTRAINTS
class Transaction_new:
    @staticmethod
    def create_transaction(inputs, outputs, signatures, create_money):
        # Extract Utxo IDs from the list of Utxo objects
        input_ids = [utxo.id for utxo in inputs]

        # Insert a row into the 'transactions' table
        transaction = Transaction(
            inputs=input_ids,  # Use only the IDs instead of the Utxo objects
            outputs=outputs,
            signatures=signatures,
            create_money=create_money,
        )
        session.add(transaction)
        session.commit()
        print(f'Transaction inserted')
        return transaction
    
    #Checking whether the address is valid or not
    @staticmethod
    def is_valid_wallet_address(address):
        return session.query(Wallet).filter_by(address=address).count() > 0

    #The following method checks whether the input parameters to the create_money method are valid
    @classmethod
    def verify_create_money_inputs(cls, authorized_address, destination_address, amount):
        if not cls.is_valid_wallet_address(authorized_address):
            return False, f"Invalid authorized address: {authorized_address}"

        if not cls.is_valid_wallet_address(destination_address):
            return False, f"Invalid destination address: {destination_address}"

        if not isinstance(amount, (int, float)) or amount <= 0:
            return False, f"Invalid amount: {amount}"

        authorized_wallet = Wallet_new.fetch_wallet_by_address(authorized_address)
        if not authorized_wallet or not authorized_wallet.authorize_address_to_create_money:
            return False, f"{authorized_address} is not authorized to create money"

        return True, None

    @staticmethod
    def sign_transaction(private_key, transaction_data):
        signature = private_key.sign(transaction_data)
        return signature
    
    @staticmethod
    def verify_signature(public_key, transaction_data_bytes, signature):
        try:
            # Verify the signature
            public_key.verify(signature, transaction_data_bytes)
            return True
        except ecdsa.BadSignatureError:
            return False
    
    @staticmethod
    def is_utxo_spent(utxo_id):
        # Check if a UTXO is spent by looking at transactions' inputs
        return session.query(Transaction).filter(Transaction.inputs.contains([utxo_id])).count() > 0
    
    #The following code verifies the source addresses and transfer details list
    @classmethod
    def validate_transfer(cls, source_addresses, transfer_details_list):
        for transfer_details in transfer_details_list:
            source_address = transfer_details.get('source_address')
            destination_address = transfer_details.get('destination_address')

            if source_address not in source_addresses:
                return False, f"Invalid source address: {source_address}"

            if not cls.is_valid_wallet_address(destination_address):
                return False, f"Invalid destination address: {destination_address}"

            amount = transfer_details.get('amount')
            if not isinstance(amount, (int, float)) or amount <= 0:
                return False, f"Invalid amount for address {destination_address}: {amount}"

        return True, None
    


#CLASS TO CREATE MONEY, TRANSFER MONEY AND CHECK BALANCE
class WalletManager:
    @classmethod
    def create_money(cls, authorized_address, destination_address, public_key,amount):
        #Verifying if the addresses are valid or not
        is_valid, error_message = Transaction_new.verify_create_money_inputs(
            authorized_address, destination_address, amount
        )

        if is_valid:
            destination_wallet = Wallet_new.fetch_wallet_by_address(destination_address)
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
            signature = Transaction_new.sign_transaction(private_key, transaction_data_bytes )
            #Verifying the signature
            is_valid_signature=Transaction_new.verify_signature(public_key,transaction_data_bytes,signature)


            #Creating transaction
            if destination_wallet and is_valid_signature:
                transaction = Transaction_new.create_transaction(
                    inputs=[],
                    outputs=[{'address': destination_address, 'amount': amount}],
                    create_money=True,
                    signatures=[signature.hex()]
                )
                #Creating utxos
                Utxo_new.create_utxo(destination_wallet.id, transaction.id, amount)

                print(f"Money created and transferred successfully from {authorized_address} to {destination_address}")
            else:
                print(f"Destination wallet not found: {destination_address}")
        else:
            print(f"Create money validation failed: {error_message}")
            

    #This code transfers the money from multiples source_addresses to multiple destination addresses
    @classmethod
    def transfer_money(cls, source_addresses, transfer_details_list, public_keys):
        #Verifying the transfer details
        is_valid, error_message = Transaction_new.validate_transfer(source_addresses, transfer_details_list)

        if is_valid:
            for transfer_details, public_key in zip(transfer_details_list,  public_keys):
                source_address = transfer_details.get('source_address')
                destination_address = transfer_details.get('destination_address')
                transfer_amount = transfer_details.get('amount', 0)

                source_wallet = Wallet_new.fetch_wallet_by_address(source_address)
                total_amount = Utxo_new.calculate_total_balance(
                    Utxo_new.fetch_available_utxos(source_wallet)
                )
                #checking if the total amount in source address is greater than the transfer amount
                if total_amount >= transfer_amount:
                    available_utxos = Utxo_new.fetch_available_utxos(source_wallet)
                    selected_utxos_ids, total_selected_amount = Utxo_new.show_utxos_and_select(
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
                    signature = Transaction_new.sign_transaction(private_key, transaction_data_bytes)
                    #Verifying the signature
                    is_valid_signature = Transaction_new.verify_signature(public_key, transaction_data_bytes, signature)
                    #Creating transaction and utxos
    
                    if is_valid_signature:
                        transaction = Transaction_new.create_transaction(
                            inputs=selected_utxos_ids,
                            outputs=[{'address': destination_address, 'amount': transfer_amount}],
                            create_money=False,
                            signatures=[signature.hex()]
                        )

                        Utxo_new.create_utxo(
                            Wallet_new.fetch_wallet_by_address(destination_address).id,
                            transaction.id,
                            transfer_amount
                        )
                    else:
                        print("Not valid signature")

                    remaining_change = total_selected_amount - transfer_amount
                    #Creating new utxo in the source address after destroying the used ones
                    if remaining_change > 0:
                        change_utxo = Utxo_new.create_utxo(source_wallet.id, transaction.id, remaining_change)
                        print(f"Change UTXO created: UTXO ID - {change_utxo.id}, Amount - {remaining_change}")

                    print(f"Money transferred successfully from {source_address} to {destination_address}.")
                else:
                    print(f"Insufficient funds in {source_address}. Available balance: {total_amount}")
        else:
            print(f"Transfer validation failed: {error_message}")
    

    #Calculating the balance in an address
    @classmethod
    def calculate_balance(cls, address):
        wallet = Wallet_new.fetch_wallet_by_address(address)

        if wallet:
            available_utxos = Utxo_new.fetch_available_utxos(wallet)
            total_balance = Utxo_new.calculate_total_balance(available_utxos)
            return total_balance
        else:
            print(f"Wallet not found for address: {address}")
            return 0.0  # Assuming a default balance of 0 if the wallet is not found


# Examples of using the WalletManager

private_key1, public_key1 = KeyPair.generate_crypto_key_pair()
private_key2, public_key2 = KeyPair.generate_crypto_key_pair()
private_key3, public_key3 = KeyPair.generate_crypto_key_pair()
private_key4, public_key4 = KeyPair.generate_crypto_key_pair()


private_key_hex4 = private_key4.to_string().hex()
mnemonic_phrase4 = KeyPair.private_key_to_mnemonic(private_key_hex4)
print(mnemonic_phrase4)
recovered_private_key_hex4=KeyPair.mnemonic_to_private_key(mnemonic_phrase4)


private_key_hex1 = private_key1.to_string().hex()
mnemonic_phrase1 = KeyPair.private_key_to_mnemonic(private_key_hex1)
print(mnemonic_phrase1)
recovered_private_key_hex1=KeyPair.mnemonic_to_private_key(mnemonic_phrase1)


address1 = KeyPair.generate_crypto_address(public_key1)
address2 = KeyPair.generate_crypto_address(public_key2)
address3 = KeyPair.generate_crypto_address(public_key3)
address4 = KeyPair.generate_crypto_address(public_key4)

Wallet_new.create_wallet(address=address1)
Wallet_new.create_wallet(address=address2) 
Wallet_new.create_wallet(address=address3)   
Wallet_new.create_wallet(address=address4)

Wallet_new.authorize_address_to_create_money(address=address4)


WalletManager.create_money(authorized_address=address4, destination_address=address1, public_key=public_key4, amount=100.0)
# WalletManager.create_money(authorized_address=address4, destination_address=address2,private_key=private_key4,public_key=public_key4, amount=200.0)

transfer_details_list = [
    {'source_address': address1, 'destination_address': address3, 'amount': 30.0},
    # {'source_address': address2, 'destination_address': address3, 'amount': 40.0},
   
]

# # Private and public keys for multiple source addresses
# private_keys_list = [private_key1, private_key3]
public_keys_list = [public_key1]

WalletManager.transfer_money(
    source_addresses=[address1, address2],
    transfer_details_list=transfer_details_list,
    public_keys=public_keys_list
)
balance = WalletManager.calculate_balance(address3)
print(f"Current balance of {address3}: {balance}")
