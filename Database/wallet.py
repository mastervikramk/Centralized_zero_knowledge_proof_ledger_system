from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Creating an SQLite database
engine = create_engine('sqlite:///wallet.db', echo=True)

# Defining a base class for declarative models
Base = declarative_base()

# Defining the Wallet model
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    authorized_to_create_money = Column(Boolean, default=False)
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
    spent_utxo_ids = Column(JSON, nullable=True)
    utxos = relationship('Utxo', back_populates='transaction')

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

class WalletManager:
    @staticmethod
    def create_table():
        # Create the tables in the database
        Base.metadata.create_all(bind=engine)
        print("Tables 'wallets', 'utxos', 'transactions' created.")

    @staticmethod
    def insert_wallet(address):
        # Insert a row into the 'wallets' table
        wallet = Wallet(address=address)
        session.add(wallet)
        session.commit()
        print(f"Wallet inserted: Address - {address}")

    @staticmethod
    def insert_utxo(wallet_id, transaction_id, amount):
        # Insert a row into the 'utxos' table
        utxo = Utxo(amount=amount, wallet_id=wallet_id, transaction_id=transaction_id)
        session.add(utxo)
        session.commit()
        print(f"UTXO inserted: Wallet ID - {wallet_id}, Transaction ID - {transaction_id}, Amount - {amount}")
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
        print(f"Transaction inserted")
        return transaction

    @staticmethod
    def fetch_wallet_by_address(address):
        # Fetch a wallet based on address
        return session.query(Wallet).filter_by(address=address).first()

    @staticmethod
    def fetch_utxos_by_wallet(wallet_id):
        # Fetch UTXOs based on wallet ID
        return session.query(Utxo).filter_by(wallet_id=wallet_id).all()

    @staticmethod
    def is_utxo_spent(utxo_id):
        # Check if a UTXO is spent by looking at the 'spent_utxo_ids' column in transactions
        return session.query(Transaction).filter(Transaction.spent_utxo_ids.contains([utxo_id])).count() > 0

    @staticmethod
    def authorize_address_to_create_money(address):
        # Authorize the wallet with the given address to create money
        wallet = WalletManager.fetch_wallet_by_address(address)
        if wallet:
            wallet.authorized_to_create_money = True
            session.commit()
            print(f"Wallet {address} authorized to create money.")
        else:
            print(f"Wallet with address {address} not found.")

    @staticmethod
    def create_money(authorized_address, destination_address, amount):
        # Check if the wallet is authorized to create money
        authorized_wallet = WalletManager.fetch_wallet_by_address(authorized_address)
        destination_wallet = WalletManager.fetch_wallet_by_address(destination_address)  # Define destination_wallet here
        if authorized_wallet and authorized_wallet.authorized_to_create_money and destination_wallet:
        
            # Create a new transaction
            transaction = WalletManager.create_transaction(inputs=[], outputs=[{'address': destination_address, 'amount': amount}],
                                                           signatures=[authorized_address], create_money=True)

            # Insert new UTXO for the destination wallet
            WalletManager.insert_utxo(destination_wallet.id, transaction.id, amount)

            print(f"Money created and transferred successfully from {authorized_address} to {destination_address}")
        else:
            print("Unauthorized to create money or wallet not found.")

    @staticmethod
    def transfer_money(source_address, destination_address, amount):
        # Fetch source and destination wallets
        source_wallet = WalletManager.fetch_wallet_by_address(source_address)
        destination_wallet = WalletManager.fetch_wallet_by_address(destination_address)

        if source_wallet and destination_wallet:
            # Fetch UTXOs from the source wallet
            source_utxos = WalletManager.fetch_utxos_by_wallet(source_wallet.id)

            # Filter out spent UTXOs
            available_utxos = [utxo for utxo in source_utxos if not WalletManager.is_utxo_spent(utxo.id)]

            # Calculate the total available balance in the source wallet
            total_amount = sum(utxo.amount for utxo in available_utxos)
            # Check if the source wallet has sufficient funds
            if total_amount >= amount:
                # Create outputs for the transaction
                outputs = [
                    {'address': destination_address, 'amount': amount},
                    {'address': source_address, 'amount': total_amount - amount}
                ]

                # Create inputs for the transaction
                inputs = []
                utxo_ids_used = set()

                # Select UTXOs to cover the transfer amount
                for utxo in available_utxos:
                    if utxo.id not in utxo_ids_used:
                        inputs.append({
                            'id': utxo.id,
                            'amount': utxo.amount
                        })
                        utxo_ids_used.add(utxo.id)

                    if sum(entry['amount'] for entry in inputs) >= amount:
                        break

                # Check if selected UTXOs cover the transfer amount
                if sum(entry['amount'] for entry in inputs) >= amount:
                    # Create a new transaction with utxo id and amount in inputs, and source address in signature
                    transaction = WalletManager.create_transaction(
                        inputs=inputs,
                        outputs=outputs,
                        signatures=[source_address],
                        create_money=False,
                        spent_utxo_ids=list(utxo_ids_used)
                    )

                    # Insert new UTXO for the destination wallet
                    WalletManager.insert_utxo(destination_wallet.id, transaction.id, amount)

                    # Leave the change UTXO in the UTXO table
                    if sum(entry['amount'] for entry in inputs) > amount:
                        change_amount = sum(entry['amount'] for entry in inputs) - amount
                        change_utxo = WalletManager.insert_utxo(source_wallet.id, transaction.id, change_amount)
                        print(f"Change UTXO created: UTXO ID - {change_utxo.id}, Amount - {change_amount}")

                    print(f"Money transferred successfully from {source_address} to {destination_address}")
                else:
                    print(f"Insufficient funds in {source_address}. Selected UTXOs do not cover the transfer amount.")
            else:
                print(f"Insufficient funds in {source_address}. Available balance: {total_amount}")
        else:
            print("Source or destination wallet not found.")

# Example usage
WalletManager.create_table()
WalletManager.insert_wallet(address="Vikram")
WalletManager.insert_wallet(address="Nandu")
WalletManager.insert_wallet(address="Money_creator")

# Authorize the wallet with address "Vikram" to create money
WalletManager.authorize_address_to_create_money(address="Money_creator")

# Create money using the authorized wallet and transfer it to another address
WalletManager.create_money(authorized_address="Money_creator", destination_address="Vikram", amount=100.0)

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
