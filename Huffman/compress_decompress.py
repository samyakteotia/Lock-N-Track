from collections import deque
from Huffman.huffman import build_frequency_table, build_huffman_tree, build_codes
from Huffman.huffman import serialize_tree, deserialize_tree, HuffmanNode

def compress_data_with_huffman(data: bytes) -> bytes:
    """Compress data using Huffman coding without modifying content"""
    if not data:
        return b""
    
    frequency = build_frequency_table(data)
    huffman_tree = build_huffman_tree(frequency)
    codes = build_codes(huffman_tree)
    
    # Serialize the Huffman tree
    tree_str = serialize_tree(huffman_tree)
    
    # Encode the actual data
    encoded_bits = []
    for byte in data:
        encoded_bits.append(codes[byte])
    
    # Convert bit string to bytes
    bit_string = ''.join(encoded_bits)
    
    # Pad the bit string to make its length a multiple of 8
    padding_length = (8 - len(bit_string) % 8) % 8
    bit_string += '0' * padding_length
    
    # Convert to bytes
    encoded_bytes = bytearray()
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        encoded_bytes.append(int(byte, 2))
    
    # Combine metadata and encoded data
    compressed_data = bytearray()
    compressed_data.append(padding_length)  # First byte is padding length
    compressed_data.extend(tree_str.encode('utf-8'))  # Then tree
    compressed_data.append(0)  # Separator
    compressed_data.extend(encoded_bytes)  # Finally the data
    
    return bytes(compressed_data)

def decompress_data_with_huffman(compressed_data: bytes) -> bytes:
    """Decompress Huffman-compressed data"""
    if not compressed_data:
        return b""
    
    # Extract padding length (first byte)
    padding_length = compressed_data[0]
    
    # Find the separator between tree and data
    separator_pos = compressed_data.find(b'\x00', 1)
    if separator_pos == -1:
        raise ValueError("Invalid compressed data format")
    
    # Extract tree string and encoded data
    tree_str = compressed_data[1:separator_pos].decode('utf-8')
    encoded_data = compressed_data[separator_pos+1:]
    
    # Rebuild the Huffman tree
    tree_data = deque(tree_str)
    huffman_tree = deserialize_tree(tree_data)
    
    # Convert encoded bytes back to bit string
    bit_string = []
    for byte in encoded_data:
        bit_string.append(f"{byte:08b}")
    bit_string = ''.join(bit_string)
    
    # Remove padding
    if padding_length > 0:
        bit_string = bit_string[:-padding_length]
    
    # Decode using the Huffman tree
    decoded_data = bytearray()
    current_node = huffman_tree
    for bit in bit_string:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = huffman_tree
    
    return bytes(decoded_data)

def compress_file(input_path: str, output_path: str) -> None:
    """Compress file without modifying content"""
    with open(input_path, 'rb') as f:
        original_data = f.read()
    
    compressed_data = compress_data_with_huffman(original_data)
    
    with open(output_path, 'wb') as f:
        f.write(compressed_data)

def decompress_file(input_path: str, output_path: str) -> None:
    """Decompress file while preserving original content"""
    with open(input_path, 'rb') as f:
        compressed_data = f.read()
    
    decompressed_data = decompress_data_with_huffman(compressed_data)
    
    with open(output_path, 'wb') as f:
        f.write(decompressed_data)