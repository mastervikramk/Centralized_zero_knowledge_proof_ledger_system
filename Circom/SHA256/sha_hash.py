import hashlib

def compute_sha256_hash(secret_input):
  # Convert integer to string (if necessary)
  if isinstance(secret_input, int):
    secret_input = str(secret_input)
  sha256_hash = hashlib.sha256(secret_input.encode()).hexdigest()
  return sha256_hash

# Example usage
secret_input = 1
sha256_result = compute_sha256_hash(secret_input)

print(f"SHA-256 hash of secretInput: {sha256_result}")

def bytes_to_binary_string(data):
  """Converts bytes data to a string of 0s and 1s."""
  binary_string = ''.join(f'{byte:08b}' for byte in data)
  return binary_string

binary_hash = bytes.fromhex(sha256_result)
binary_string = bytes_to_binary_string(binary_hash)
print(f"SHA-256 hash in 0s and 1s: {binary_string}")

def binary_to_hex(binary_string):
  """Converts a binary string to a hexadecimal string."""
  hex_string = hex(int(binary_string, 2))[2:].zfill(len(binary_string) // 4)
  return hex_string

long_binary_string = "0110101110000110101100100111001111111111001101001111110011100001100111010110101110000000010011101111111101011010001111110101011101000111101011011010010011101010101000100010111100011101010010011100000000011110010100101101110110110111100001110101101101001011"  # Your full binary string
chunk_size = 64
hex_array = [binary_to_hex(long_binary_string[i:i+chunk_size]) for i in range(0, len(long_binary_string), chunk_size)]

print(hex_array)
