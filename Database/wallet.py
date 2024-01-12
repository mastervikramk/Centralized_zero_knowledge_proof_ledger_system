from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON, Boolean, MetaData
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
    utxos = relationship('Utxo', back_populates='transaction')

# Create the table in the database
metadata = MetaData()
Base.metadata.create_all(bind=engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

class WalletManager:
    @staticmethod
    def create_table():
        # Create the table in the database
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
    def insert_utxo(wallet_id, amount):
        # Insert a row into the 'utxos' table
        utxo = Utxo(amount=amount, wallet_id=wallet_id)
        session.add(utxo)
        session.commit()
        print(f"UTXO inserted: Wallet ID - {wallet_id}, Amount - {amount}")

    @staticmethod
    def fetch_row_by_id(wallet_id):
        # Fetch a row based on ID
        wallet = session.query(Wallet).get(wallet_id)
        if wallet:
            print(f"Wallet ID: {wallet.id}, Address: {wallet.address}")
        else:
            print(f"No wallet found with ID {wallet_id}")

    @staticmethod
    def fetch_rows_by_condition(condition):
        # Fetch rows based on a condition
        wallets = session.query(Wallet).filter(condition).all()
        if wallets:
            print("Wallets matching the condition:")
            for wallet in wallets:
                print(f"ID: {wallet.id}, Address: {wallet.address}")
        else:
            print("No wallets found matching the condition.")

# Example usage
WalletManager.create_table()
WalletManager.insert_wallet(address="xyz_address")
WalletManager.insert_utxo(wallet_id=1, amount=50.0)

# Fetch by ID
WalletManager.fetch_row_by_id(wallet_id=1)

# Fetch by condition
WalletManager.fetch_rows_by_condition(Wallet.id == 1)
