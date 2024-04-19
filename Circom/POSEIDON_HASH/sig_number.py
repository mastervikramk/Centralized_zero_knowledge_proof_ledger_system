import hashlib
import base64

signature_hex ="c90c534641951d2d9cf02fedaeac8a157bd214a4a4be2cd37c94047cfceb758da69d1bf277f6929afa6e1e086de46160"  # Example hexadecimal signature

# Convert signature to bytes
signature_bytes = bytes.fromhex(signature_hex)

# Hash the signature using SHA-256
hashed_signature = hashlib.sha256(signature_bytes).digest()

# Encode the hashed signature using Base64
encoded_signature = base64.b64encode(hashed_signature)

#We can store the encoded signature and while passing input we will pass only signature number

# Decode the Base64-encoded signature
decoded_signature = base64.b64decode(encoded_signature)

# Interpret the decoded signature as a number
signature_number = int.from_bytes(decoded_signature, byteorder='big')

print("Signature as number:", signature_number)

