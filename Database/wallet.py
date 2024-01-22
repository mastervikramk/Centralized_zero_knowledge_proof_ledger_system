from sqlalchemy import create_engine, Integer, Column, String, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# Creating an SQLite database
engine = create_engine('sqlite:///wallet3.db', echo=True)

# Defining a base class for declarative models
Base = declarative_base()

# Defining the Wallet model
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    authorize_address_to_create_money = Column(Boolean, default=False)
    utxos = relationship('Utxo', back_populates='wallet')

# Defining the UTXO model
class Utxo(Base):
    __tablename__ = 'utxos'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    wallet = relationship('Wallet', back_populates='utxos')
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    transaction = relationship('Transaction', back_populates='utxos')

# Defining the Transaction model
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON, nullable=False)
    signatures = Column(JSON, nullable=False)
    create_money = Column(Boolean, nullable=False)
    spent_utxo_ids = Column(JSON)  # Add the spent_utxo_ids column here
    utxos = relationship('Utxo', back_populates='transaction')

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
    def create_transaction(inputs, outputs, signatures, create_money, spent_utxo_ids=None):
        # Insert a row into the 'transactions' table
        transaction = Transaction(
            inputs=inputs,
            outputs=outputs,
            signatures=signatures,
            create_money=create_money,
            spent_utxo_ids=spent_utxo_ids
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

    @staticmethod
    def create_money(authorized_address, destination_address, amount):
        # Check if the wallet is authorized to create money
        authorized_wallet = WalletManager.fetch_wallet_by_address(authorized_address)
        destination_wallet = WalletManager.fetch_wallet_by_address(destination_address)

        if authorized_wallet and authorized_wallet.authorize_address_to_create_money and destination_wallet:
            # Create a new transaction
            transaction = WalletManager.create_transaction(
                inputs=[],
                outputs=[{'address': destination_address, 'amount': amount}],
                signatures=[authorized_address],
                create_money=True
            )

            # Insert new UTXO for the destination wallet
            WalletManager.create_utxo(destination_wallet.id, transaction.id, amount)

            print(f"Money created and transferred successfully from {authorized_address} to {destination_address}")
        else:
            print("Unauthorized to create money or wallet not found.")
 

    @staticmethod
    def is_utxo_spent(utxo_id):
        # Check if a UTXO is spent by looking at the 'spent_utxo_ids' column in transactions
        return session.query(Transaction).filter(Transaction.spent_utxo_ids.contains([utxo_id])).count() > 0

    @staticmethod
    def fetch_available_utxos(source_wallet):
        source_utxos = WalletManager.fetch_utxos_by_wallet(source_wallet.id)
        return [utxo for utxo in source_utxos if not WalletManager.is_utxo_spent(utxo.id)]

    @staticmethod
    def calculate_total_balance(utxos):
        return sum(utxo.amount for utxo in utxos)

    
    @staticmethod
    def prepare_transaction_data(available_utxos, destination_address, source_address, amount):
        inputs = []
        utxo_ids_used = set()

        for utxo in available_utxos:
            if utxo.id not in utxo_ids_used:
                inputs.append({
                    'id': utxo.id,
                    'amount': utxo.amount
                })
                utxo_ids_used.add(utxo.id)

            input_amount = sum(entry['amount'] for entry in inputs)
            if input_amount >= amount:
                break

        # Convert set to list before storing in JSON column
        utxo_ids_used_list = list(utxo_ids_used)

        # Create outputs for the transaction
        outputs = [
            {'address': destination_address, 'amount': amount},
            {'address': source_address, 'amount': input_amount - amount}
        ]
        
        input_amount = sum(entry['amount'] for entry in inputs)
        output_amount = sum(output['amount'] for output in outputs)

        if input_amount==output_amount:
            print("INPUT AMOUNT = OUTPUT AMOUNT (VALIDATED)")
        return inputs, outputs, utxo_ids_used_list,input_amount
    
    @staticmethod
    def transfer_money(source_address, destination_address, amount):
        source_wallet = WalletManager.fetch_wallet_by_address(source_address)
        destination_wallet = WalletManager.fetch_wallet_by_address(destination_address)

        if source_wallet and destination_wallet:
            available_utxos = WalletManager.fetch_available_utxos(source_wallet)
            total_amount = WalletManager.calculate_total_balance(available_utxos)

            if total_amount >= amount:
                inputs, outputs, utxo_ids_used_list,input_amount = WalletManager.prepare_transaction_data(
                    available_utxos, destination_address, source_address, amount
                )

                transaction = WalletManager.create_transaction(
                    inputs=inputs,
                    outputs=outputs,
                    signatures=[source_address],
                    create_money=False,
                    spent_utxo_ids=utxo_ids_used_list
                )

                WalletManager.create_utxo(destination_wallet.id, transaction.id, amount)

                if total_amount > amount:
                    change_amount = input_amount - amount
                    change_utxo = WalletManager.create_utxo(source_wallet.id, transaction.id, change_amount)
                    print(f"Change UTXO created: UTXO ID - {change_utxo.id}, Amount - {change_amount}")

                print(f"Money transferred successfully from {source_address} to {destination_address}")
            else:
                print(f"Insufficient funds in {source_address}. Available balance: {total_amount}")
        else:
            print("Source or destination wallet not found.")


# Examples of using the WalletManager

WalletManager.create_wallet(address="Vikram")
WalletManager.create_wallet(address="Nandu")
WalletManager.create_wallet(address="Money_creator")

WalletManager.authorize_address_to_create_money(address="Money_creator")

# Create money using the authorized wallet and transfer it to another address
WalletManager.create_money(authorized_address="Money_creator", destination_address="Vikram", amount=100.0)
WalletManager.create_money(authorized_address="Money_creator", destination_address="Nandu", amount=200.0)

# Transfer money from source_address to destination_address
WalletManager.transfer_money(source_address="Vikram", destination_address="Nandu", amount=50.0)

# Add another transaction
WalletManager.transfer_money(source_address="Nandu", destination_address="Vikram", amount=30.0)

# Add another transaction
WalletManager.transfer_money(source_address="Vikram", destination_address="Nandu", amount=10.0)

# Add another transaction
WalletManager.transfer_money(source_address="Nandu", destination_address="Vikram", amount=90.0)  # Output will show Insufficient balance

# Create money using the authorized wallet and transfer it to another address
WalletManager.create_money(authorized_address="Money_creator", destination_address="Nandu", amount=100.0)
