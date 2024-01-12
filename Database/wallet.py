from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an SQLite database
engine = create_engine('sqlite:///wallet.db', echo=True)

# Define a base class for declarative models
Base = declarative_base()

# Define the Wallet model
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    balance = Column(Float, default=0.0)

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
        print("Table 'wallets' created.")

    @staticmethod
    def insert_row(address, balance):
        # Insert a row into the 'wallets' table
        wallet = Wallet(address=address, balance=balance)
        session.add(wallet)
        session.commit()
        print(f"Row inserted: Address - {address}, Balance - {balance}")

    @staticmethod
    def fetch_row_by_id(wallet_id):
        # Fetch a row based on ID
        wallet = session.query(Wallet).get(wallet_id)
        if wallet:
            print(f"Wallet ID: {wallet.id}, Address: {wallet.address}, Balance: {wallet.balance}")
        else:
            print(f"No wallet found with ID {wallet_id}")

    @staticmethod
    def fetch_rows_by_condition(condition):
        # Fetch rows based on a condition
        wallets = session.query(Wallet).filter(condition).all()
        if wallets:
            print("Wallets matching the condition:")
            for wallet in wallets:
                print(f"ID: {wallet.id}, Address: {wallet.address}, Balance: {wallet.balance}")
        else:
            print("No wallets found matching the condition.")


WalletManager.create_table()
WalletManager.insert_row("nandu...", 100.0)
WalletManager.insert_row("vikram...", 300.0)
WalletManager.insert_row("vinay...", 500.0)
WalletManager.insert_row("prof...", 900.0)
WalletManager.fetch_row_by_id(1)
WalletManager.fetch_rows_by_condition(Wallet.balance > 800.0)


