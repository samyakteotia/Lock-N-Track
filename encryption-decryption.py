import os
from XOR_Encrypt.encrypt_decrypt import encrypt_file_with_password
from XOR_Encrypt.encrypt_decrypt import decrypt_file_with_password_attempts
from Huffman.compress_decompress import compress_file
from Huffman.compress_decompress import decompress_file



def get_file_path_from_user() -> str:
    file_path = input("📄 Enter the file name (including extension): ").strip()
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        exit(1)
    return file_path


def main():
    print("=== 🔒 File Utility Tool (Encrypt / Decrypt / Compress / Decompress) ===")
    user_choice = input("Enter 'E' to Encrypt, 'D' to Decrypt, 'C' to Compress, or 'X' to Decompress a file: ").strip().lower()

    if user_choice not in ['e', 'd', 'c', 'x']:
        print("Invalid choice. Please enter 'E', 'D', 'C', or 'X'.")
        return

    file_path = get_file_path_from_user()

    if user_choice == 'e':
        password = input("🔑 Enter a password to encrypt the file: ")
        encrypt_file_with_password(file_path, password)
    elif user_choice == 'd':
        decrypt_file_with_password_attempts(file_path)
    elif user_choice == 'c':
        compress_file(file_path)
    elif user_choice == 'x':
        decompress_file(file_path)


if __name__ == "__main__":
    main()