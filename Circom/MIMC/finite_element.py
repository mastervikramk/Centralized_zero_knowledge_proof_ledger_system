import hashlib

# Define the characteristics of the finite field
field_size = 13  # Example prime field size

class FieldEncoder:
    def __init__(self, field_size):
        self.field_size = field_size

    def _string_to_field_element(self, string):
        # Hash the string using SHA-256 and convert to integer
        hashed_value = int.from_bytes(hashlib.sha256(string.encode()).digest(), byteorder='big')
        # Reduce modulo the field size
        field_element = hashed_value % self.field_size
        return field_element

    def _integer_to_field_element(self, integer):
        # Reduce modulo the field size
        field_element = integer % self.field_size
        return field_element

    def encode_inputs(self, input_utxo1, input_utxo2, output_utxo1, output_utxo2, signature1, signature2):
        field_elements = {}
        field_elements['input_utxo1'] = self._integer_to_field_element(input_utxo1)
        field_elements['input_utxo2'] = self._integer_to_field_element(input_utxo2)
        field_elements['output_utxo1'] = self._integer_to_field_element(output_utxo1)
        field_elements['output_utxo2'] = self._integer_to_field_element(output_utxo2)
        field_elements['signature1'] = self._string_to_field_element(signature1)
        field_elements['signature2'] = self._string_to_field_element(signature2)
        return field_elements

def main():
    # Example usage
    encoder = FieldEncoder(field_size)
    input_utxo1 = 1
    input_utxo2 = 2
    output_utxo1 = 3
    output_utxo2 = 4
    signature1 = "c90c534641951d2d9cf02fedaeac8a157bd214a4a4be2cd37c94047cfceb758da69d1bf277f6929afa6e1e086de46160"
    signature2 = "5b270a90f3404d53d00541dee19ec8348f212e9fc2a15e448acaa435b05a6b4a8a4ca9131333f0932fdde0a4589e9d75"

    field_elements = encoder.encode_inputs(input_utxo1, input_utxo2, output_utxo1, output_utxo2, signature1, signature2)

    print("Field elements:", field_elements)

if __name__ == "__main__":
    main()
