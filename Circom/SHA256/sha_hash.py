import hashlib

def compute_sha256_hash(utxo_id):
    # Concatenate the inputs into a single string
    input_string = f"{utxo_id}"

    # Compute the SHA-256 hash
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()

    return sha256_hash

# Example usage
utxo_id = 0


sha256_result = compute_sha256_hash(utxo_id)
print(f"SHA-256 hash: {sha256_result}")
