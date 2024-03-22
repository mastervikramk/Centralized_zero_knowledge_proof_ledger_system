def add_commas(input_string):
    # Reverse the input string
    reversed_string = input_string[::-1]
    
    # Split the reversed string into groups of three characters
    groups_of_three = [reversed_string[i:i+1] for i in range(0, len(reversed_string), 1)]
    
    # Join the groups with commas and reverse the result
    result = ','.join(groups_of_three)[::-1]
    
    return result

# Example usage:
input_string = "0110101110000110101100100111001111111111001101001111110011100001100111010110101110000000010011101111111101011010001111110101011101000111101011011010010011101010101000100010111100011101010010011100000000011110010100101101110110110111100001110101101101001011"
comma_separated = add_commas(input_string)
print(comma_separated)
