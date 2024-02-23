from models import Wallet
from keys import KeyPair
from wallet_manager import WalletManager

# Examples of using the WalletManager
keypair1= KeyPair()
keypair2= KeyPair()
keypair3= KeyPair()
keypair4= KeyPair()

private_key1, public_key1 = keypair1.private_key,keypair1.public_key
private_key2, public_key2 = keypair2.private_key,keypair2.public_key
private_key3, public_key3 = keypair3.private_key,keypair3.public_key
private_key4, public_key4 = keypair4.private_key,keypair4.public_key

mnemonic_phrase4 = keypair4.private_key_to_mnemonic()
print(mnemonic_phrase4)
recovered_private_key_hex4=KeyPair.mnemonic_to_private_key(mnemonic_phrase4)


mnemonic_phrase1 = keypair1.private_key_to_mnemonic()
print(mnemonic_phrase1)
recovered_private_key_hex1=KeyPair.mnemonic_to_private_key(mnemonic_phrase1)

address1=keypair1.create_address()
address2=keypair2.create_address()
address3=keypair3.create_address()
address4=keypair4.create_address()

Wallet1=Wallet(address=address1)
Wallet2=Wallet(address=address2) 
Wallet3=Wallet(address=address3)   
Wallet4=Wallet(address=address4)

Wallet4.authorize_address_to_create_money(address4)

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
balance = WalletManager.balance(address3)
print(f"Current balance of {address3}: {balance}")