import os
def xor_encrypt_decrypt_data(input_data: bytes, key: bytearray) -> bytes:
    encrypted_or_decrypted = bytearray()
    for index in range(len(input_data)):
        byte = input_data[index]
        key_byte = key[index % len(key)]
        result_byte = byte ^ key_byte
        encrypted_or_decrypted.append(result_byte)
    return bytes(encrypted_or_decrypted)

def encrypt_file_with_password(file_path: str, password: str) -> None:
    with open(file_path, "rb") as file:
        file_content = file.read()
    key = create_key_from_password(password, len(file_content))
    encrypted_content = xor_encrypt_decrypt_data(file_content, key)
    with open(file_path, "wb") as file:
        file.write(encrypted_content)
    print(f"✅ File '{file_path}' encrypted successfully.")


def decrypt_file_with_password_attempts(file_path: str, max_attempts: int = 3) -> None:
    for attempt in range(1, max_attempts + 1):
        entered_password = input(f"🔐 Attempt {attempt}/{max_attempts} - Enter password to decrypt: ")
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        key = create_key_from_password(entered_password, len(encrypted_data))
        decrypted_data = xor_encrypt_decrypt_data(encrypted_data, key)
        try:
            decrypted_data.decode('utf-8')
            with open(file_path, "wb") as file:
                file.write(decrypted_data)
            print(f"✅ File '{file_path}' decrypted successfully.")
            return
        except UnicodeDecodeError:
            print("❌ Incorrect password.")
    print("🚫 Too many failed attempts. Deleting file for security.")
    os.remove(file_path)

def create_key_from_password(password: str, required_length: int) -> bytearray:
    base_value = sum(ord(char) for char in password)
    key_stream = bytearray()
    for i in range(required_length):
        key_byte = (base_value + i * 17) % 256
        key_stream.append(key_byte)
    return key_stream