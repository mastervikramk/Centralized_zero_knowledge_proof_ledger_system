import hashlib

import json

def compute_sha256_hash(secret_input):
    # Convert the input array to a JSON string
    input_json = json.dumps({"secretInput": secret_input})

    # Compute the SHA-256 hash
    sha256_hash = hashlib.sha256(input_json.encode()).hexdigest()

    return sha256_hash

# Example input
secret_input = ["1", "2", "3", "4", "5", "6", "7", "8"]

# Compute the SHA-256 hash
sha256_result = compute_sha256_hash(secret_input)

print(f"SHA-256 hash of secretInput: {sha256_result}")

