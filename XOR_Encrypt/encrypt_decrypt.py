import os

def xor_encrypt_decrypt_data(input_data: bytes, key: bytearray) -> bytes:
    encrypted_or_decrypted = bytearray()
    for index in range(len(input_data)):
        byte = input_data[index]
        key_byte = key[index % len(key)]
        result_byte = byte ^ key_byte
        encrypted_or_decrypted.append(result_byte)
    return bytes(encrypted_or_decrypted)

def create_key_from_password(password: str, required_length: int) -> bytearray:
    """Create encryption key from password (fixed to handle both str and bytes)"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    base_value = sum(byte for byte in password)
    key_stream = bytearray()
    for i in range(required_length):
        key_byte = (base_value + i * 17) % 256
        key_stream.append(key_byte)
    return key_stream

def encrypt_file_with_password(file_path: str, password: str) -> None:
    """Encrypt file with password (fixed to handle binary data properly)"""
    with open(file_path, 'rb') as file:
        file_content = file.read()
    key = create_key_from_password(password, len(file_content))
    encrypted_content = xor_encrypt_decrypt_data(file_content, key)
    with open(file_path, 'wb') as file:
        file.write(encrypted_content)

def decrypt_file_with_password_attempts(file_path: str, password: str, max_attempts: int = 3) -> None:
    """Decrypt file with password attempts (fixed error handling)"""
    for attempt in range(1, max_attempts + 1):
        try:
            with open(file_path, 'rb') as file:
                encrypted_data = file.read()
            key = create_key_from_password(password, len(encrypted_data))
            decrypted_data = xor_encrypt_decrypt_data(encrypted_data, key)
            
            # Test if decryption was successful
            if len(decrypted_data) == 0 or not all(32 <= byte <= 126 or byte in {9,10,13} for byte in decrypted_data[:100]):
                raise ValueError("Invalid decryption result")
                
            with open(file_path, 'wb') as file:
                file.write(decrypted_data)
            return
        except Exception as e:
            if attempt == max_attempts:
                os.remove(file_path)
                raise ValueError(f"Failed after {max_attempts} attempts")