import os
from XOR_Encrypt.encrypt_decrypt import encrypt_file_with_password
from XOR_Encrypt.encrypt_decrypt import decrypt_file_with_password_attempts
from Huffman.compress_decompress import compress_file
from Huffman.compress_decompress import decompress_file
from version_control.vcs import init_vcs, snapshot, revert_to_snapshot


def get_file_path_from_user() -> str:
    file_path = input("Enter the file name (including extension): ").strip()
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found.")
        exit(1)
    return file_path


def main():
    print("=== 🔐 File Utility Tool ===")
    print("Options:")
    print("  E - Encrypt")
    print("  D - Decrypt")
    print("  C - Compress")
    print("  X - Decompress")
    print("  I - Init VCS")
    print("  S - Snapshot")
    print("  R - Revert to Snapshot")

    user_choice = input("Enter your choice: ").strip().lower()

    if user_choice not in ['e', 'd', 'c', 'x', 'i', 's', 'r']:
        print("Invalid choice. Please enter a valid option.")
        return

    if user_choice == 'e':
        file_path = get_file_path_from_user()
        password = input("🔑 Enter a password to encrypt the file: ")
        encrypt_file_with_password(file_path, password)

    elif user_choice == 'd':
        file_path = get_file_path_from_user()
        decrypt_file_with_password_attempts(file_path)

    elif user_choice == 'c':
        file_path = get_file_path_from_user()
        compress_file(file_path)

    elif user_choice == 'x':
        file_path = get_file_path_from_user()
        decompress_file(file_path)

    elif user_choice == 'i':
        init_vcs()

    elif user_choice == 's':
        snapshot('.')

    elif user_choice == 'r':
        hash_digest = input("🔁 Enter the snapshot hash to revert to: ").strip()
        revert_to_snapshot(hash_digest)


if __name__ == "__main__":
    main()
