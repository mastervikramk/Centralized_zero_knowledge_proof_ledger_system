from sqlalchemy import create_engine, Integer, Column, String, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import inquirer

# Creating an SQLite database
engine = create_engine('sqlite:///wallet.db', echo=True)

# Defining a base class for declarative models
Base = declarative_base()


# Defining the Wallet model
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    authorize_address_to_create_money = Column(Boolean, default=False)
    #utxos represent all the utxos associated with wallet id
    utxos = relationship('Utxo', back_populates='wallet') #can access utxos associated with the wallet


# Defining the UTXO model
class Utxo(Base):
    __tablename__ = 'utxos'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    wallet_id = Column(Integer, ForeignKey('wallets.id'))#Represent the wallet where the utxo is created
    #wallet retpresent wallet(id and address) associated with the utxo id
    wallet = relationship('Wallet', back_populates='utxos')# can access wallets associated with the utxo
    transaction_id = Column(Integer, ForeignKey('transactions.id'))#Represent the transaction during which the utxo is created
    #transaction represent transaction data associated with the utxo id
    transaction = relationship('Transaction', back_populates='utxos')#can access transactions associated with the utxo

# Defining the Transaction model
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    #inputs contain the utxos(utxo id) used as input
    inputs = Column(JSON)
    #outputs contain destination address and amount
    outputs = Column(JSON, nullable=False)
    signatures = Column(JSON, nullable=False)
    create_money = Column(Boolean, nullable=False)
    #Here utxos represent all the utxos associated with transaction id
    utxos = relationship('Utxo', back_populates='transaction')# can access utxos associated with the transaction


# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

class WalletManager:
    @staticmethod
    def create_wallet(address):
        # Inserting a row into the "wallets" table
        wallet = Wallet(address=address)
        session.add(wallet)
        session.commit()
        print(f"Wallet inserted: Address - {address}")

    @staticmethod
    def create_utxo(wallet_id, transaction_id, amount):
        # Insert a row into the 'utxos' table
        utxo = Utxo(wallet_id=wallet_id, transaction_id=transaction_id, amount=amount)
        session.add(utxo)
        session.commit()
        print(f"UTXO inserted: Wallet ID - {wallet_id}, Amount - {amount}")
        return utxo

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


    @staticmethod
    def fetch_wallet_by_address(address):
         # Fetch a wallet based on address
        return session.query(Wallet).filter_by(address=address).first()

    @staticmethod
    def fetch_utxos_by_wallet(wallet_id):
         # Fetch UTXOs based on wallet ID
        return session.query(Utxo).filter(Utxo.wallet_id == wallet_id).all()

    @staticmethod
    def authorize_address_to_create_money(address):
         # Authorize the wallet with the given address to create money
        wallet = WalletManager.fetch_wallet_by_address(address)
        if wallet:
            wallet.authorize_address_to_create_money = True
            session.commit()
            print(f"Wallet {address} authorized to create money.")
        else:
            print(f"Wallet with the address {address} not found.")

    #The following method checks whether the input parameters to the create_money method are valid
    @classmethod
    def validate_create_money_inputs(cls, authorized_address, destination_address, amount):
        if not cls.is_valid_wallet_address(authorized_address):
            return False, f"Invalid authorized address: {authorized_address}"

        if not cls.is_valid_wallet_address(destination_address):
            return False, f"Invalid destination address: {destination_address}"

        if not isinstance(amount, (int, float)) or amount <= 0:
            return False, f"Invalid amount: {amount}"

        authorized_wallet = cls.fetch_wallet_by_address(authorized_address)
        if not authorized_wallet or not authorized_wallet.authorize_address_to_create_money:
            return False, f"{authorized_address} is not authorized to create money"

        return True, None
    
    #The following method allows to create money
    @classmethod
    def create_money(cls, authorized_address, destination_address, amount):
        is_valid, error_message = cls.validate_create_money_inputs(
            authorized_address, destination_address, amount
        )

        if is_valid:
            destination_wallet = cls.fetch_wallet_by_address(destination_address)
            if destination_wallet:
                transaction = cls.create_transaction(
                    inputs=[],
                    outputs=[{'address': destination_address, 'amount': amount}],
                    signatures=[authorized_address],
                    create_money=True
                )
                cls.create_utxo(destination_wallet.id, transaction.id, amount)
                print(f"Money created and transferred successfully from {authorized_address} to {destination_address}")
            else:
                print(f"Destination wallet not found: {destination_address}")
        else:
            print(f"Create money validation failed: {error_message}")

    @staticmethod
    def is_utxo_spent(utxo_id):
        # Check if a UTXO is spent by looking at transactions' inputs
        return session.query(Transaction).filter(Transaction.inputs.contains([utxo_id])).count() > 0

    @staticmethod
    def fetch_available_utxos(source_wallet):
        #Fetching all the utxos associated will the wallet
        source_utxos = WalletManager.fetch_utxos_by_wallet(source_wallet.id)
        return [utxo for utxo in source_utxos if not WalletManager.is_utxo_spent(utxo.id)]

    @staticmethod
    def calculate_total_balance(utxos):
        #Calculating total balance of all the utxos
        return sum(utxo.amount for utxo in utxos)
    
    #List which will keep the already selected utxos 
    used_utxos = []
    
    #The following method is for selecting the particular utxos for transaction
    @classmethod
    def show_utxos_and_select(cls, available_utxos, transfer_amount):
        # Filter out used UTXOs
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

        print("\nSelected UTXOs:")
        for selected_utxo in selected_utxos:
            print(f"UTXO ID: {selected_utxo.id}, Amount: {selected_utxo.amount}")

        if total_selected_amount >= transfer_amount:
            return selected_utxos, total_selected_amount
        else:
            print("\nSelected UTXOs do not cover the transfer amount. Please try again.")
            return cls.show_utxos_and_select(available_utxos, transfer_amount)
    
    #Checking whether the address is valid or not
    @staticmethod
    def is_valid_wallet_address(address):
        return session.query(Wallet).filter_by(address=address).count() > 0
    
    #Checking whther the transfer details are valid or not
    @classmethod
    def is_valid_transfer_details(cls, transfer_details):
        for detail in transfer_details:
            destination_address = detail.get('address')
            amount = detail.get('amount')

            if not cls.is_valid_wallet_address(destination_address):
                return False, f"Invalid destination address: {destination_address}"

            if not isinstance(amount, (int, float)) or amount <= 0:
                return False, f"Invalid amount for address {destination_address}: {amount}"

        return True, None
    
    #Checking whether input parameters to the transfer_money method are valid or not
    @classmethod
    def validate_transfer(cls, source_address, transfer_details):
        if not cls.is_valid_wallet_address(source_address):
            return False, f"Invalid source address: {source_address}"

        is_valid_details, error_message = cls.is_valid_transfer_details(transfer_details)
        if not is_valid_details:
            return False, error_message

        return True, None
    
    #The following method allows to transfer money from one address to the many destination addresses
    @staticmethod
    def transfer_money(source_address, transfer_details):
        is_valid, error_message = WalletManager.validate_transfer(source_address, transfer_details)
        #validaation check
        if is_valid:
            source_wallet = WalletManager.fetch_wallet_by_address(source_address)
            total_amount = WalletManager.calculate_total_balance(
                WalletManager.fetch_available_utxos(source_wallet)
            )
            #Amount to be transfered
            transfer_amount = sum(detail['amount'] for detail in transfer_details)
            
            #checking whether the total balance in source wallet is more than the transfer amount
            if total_amount >= transfer_amount:
                available_utxos = WalletManager.fetch_available_utxos(source_wallet)
                selected_utxos_ids, total_selected_amount = WalletManager.show_utxos_and_select(
                    available_utxos, transfer_amount
                )
                #creating transaction
                transaction = WalletManager.create_transaction(
                    inputs=selected_utxos_ids,
                    outputs=[
                        {'address': detail['address'], 'amount': detail['amount']}
                        for detail in transfer_details
                    ],
                    signatures=[source_address],
                    create_money=False
                )
                #Destination addresses and amounts to be transfered
                for detail in transfer_details:
                    destination_address = detail['address']
                    amount = detail['amount']
                    WalletManager.create_utxo(
                        WalletManager.fetch_wallet_by_address(destination_address).id,
                        transaction.id,
                        amount
                    )
                #Total selected amount is the sum of utxos selected from which amount is to be transfered
                remaining_change = total_selected_amount - transfer_amount
                #Remaining change is left amount(new utxo to be created to the source address)
                if remaining_change > 0:
                    change_utxo = WalletManager.create_utxo(source_wallet.id, transaction.id, remaining_change)
                    print(f"Change UTXO created: UTXO ID - {change_utxo.id}, Amount - {remaining_change}")

                print(f"Money transferred successfully from {source_address} to multiple addresses.")
            else:
                print(f"Insufficient funds in {source_address}. Available balance: {total_amount}")
        else:
            print(f"Transfer validation failed: {error_message}")

# Examples of using the WalletManager

WalletManager.create_wallet(address="Vikram")
WalletManager.create_wallet(address="Nandu") 
WalletManager.create_wallet(address="Vinay")
WalletManager.create_wallet(address="Money_creator")

WalletManager.authorize_address_to_create_money(address="Money_creator")

WalletManager.create_money(authorized_address="Money_creator", destination_address="Vikram", amount=100.0)
WalletManager.create_money(authorized_address="Money_creator", destination_address="Nandu", amount=200.0)

#Transfer to more than one address
transfer_details = [
    {'address': "Nandu", 'amount': 50.0},
    {'address': "Vinay", 'amount': 30.0},
]

WalletManager.transfer_money(source_address="Vikram", transfer_details=transfer_details)
WalletManager.transfer_money(source_address="Nandu", transfer_details=[{'address':"Vikram",'amount':140.00}])
WalletManager.transfer_money(source_address="Nandu", transfer_details=[{'address':"Vinay",'amount':50.0}])
