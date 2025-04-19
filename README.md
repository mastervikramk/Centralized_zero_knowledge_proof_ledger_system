# 🛒 Centralized System for Buying and Shipping Goods with Secure Payments

## 📘 What This Project Does

This project simulates a system where people can **buy and sell goods** and have them **shipped securely**. It works like a **centralized version of a blockchain** and uses:

- **Zero-Knowledge Proofs (ZKP)** to check if a transaction is valid without revealing private info  
- **Wallets with secret phrases (mnemonics)** for signing and sending money  
- A **notary (central authority)** to approve transactions  
- **Smart contract-style rules** to automatically pay sellers after delivery  
- A way of managing money like **Bitcoin’s UTXO system**

---

## 🔐 Main Ideas

- **Ledger**: A single, secure place to record all transactions  
- **Wallets**: Each user has a wallet with a unique address and a secret phrase  
- **ZKP (Zero-Knowledge Proofs)**: Used to prove a transaction is valid without exposing details  
- **Auto Payments**: Once a product is delivered, the system sends money to the seller  
- **UTXO Model**: Like in Bitcoin, money is split into pieces that are used and created in each transaction

---

## 💸 How Payments Work

1. **Create Wallets**  
   - Each user gets a wallet with a unique address and a secret phrase to sign transactions.

2. **Bank Creates Money**  
   - A special wallet (the bank) can create money as UTXOs (Unspent Transaction Outputs).

3. **Transfer Money**  
   - Users send money by using existing UTXOs and signing the transaction with their secret phrase.

4. **Auto Payment After Delivery**  
   - When a driver confirms delivery, the system automatically pays the seller using smart contract logic.

---

## 📂 Project Structure
. ├── BitcoinParsing/ │ └── parse_blocks.py # Parses Bitcoin blocks for reference or integration │ ├── circom_program_and_proof/ │ ├── circuit.circom # Circom code for ZKP generation │ ├── input.json # Sample input for the ZKP circuit │ ├── proof_generator.js # JS code to generate and verify zero-knowledge proofs │ └── verification_key.json # Verification key for the ZKP system │ ├── Database/ │ ├── models.py # DB schema for users, products, transactions, etc. │ ├── keys.py # Wallet key generation functions │ ├── wallet_manager.py # UTXO creation and money transfer logic │ ├── wallet.py # Unified version of wallet-related functionality │ └── test_wallet.py # Pytest code for testing wallet.py │ ├── requirements.txt # Python package dependencies └── README.md # Project documentation (this file)
