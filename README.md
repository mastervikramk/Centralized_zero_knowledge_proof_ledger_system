# Centralized Blockchain-Like System for Goods Purchase and Shipment

## 📘 Overview

This project simulates a **centralized blockchain-inspired system** for purchasing goods and managing shipments. The system integrates:

- **Zero-Knowledge Proofs (ZKP)** for transaction validation,
- **Digital signatures** and **mnemonic-based wallets** for authentication,
- A **central notary** for verification,
- A **smart contract-like auto-payment mechanism** upon successful delivery,
- And a **UTXO-based transaction model** for money management.

---

## 🔐 Key Concepts

- **Centralized Ledger**: All transactions are recorded in a tamper-evident ledger.
- **Wallets & Mnemonics**: Each user has a wallet with a unique address and mnemonic for signing.
- **Zero-Knowledge Proofs**: Proofs validate transactions without revealing sensitive data.
- **Smart Contracts**: Automatic payment execution after delivery is confirmed.
- **Digital Currency**: Modeled using UTXOs for traceable and secure transactions.

---

## 💸 Wallet & Payment Flow

1. **Wallet Creation**:
   - Unique wallet address and mnemonic phrase per user.
   - Wallets can sign transactions using mnemonic-based authentication.

2. **Central Bank Setup**:
   - A dedicated bank address mints digital money in the form of UTXOs.

3. **Money Transfer**:
   - Users consume existing UTXOs to create new ones.
   - Transactions are signed using mnemonics and verified before ledger update.

4. **Automatic Payout**:
   - After delivery confirmation by the driver, payment UTXOs are transferred to the seller automatically.

---






