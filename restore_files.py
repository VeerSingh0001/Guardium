from cryptography.fernet import Fernet

key = "BY3VYM-i5pek9UGeijYGvNobJ_sr2yArso6bzwif66E="
def decrypt_file(encrypted_file_path, restore_path, key_file=key):
    fernet = Fernet(key)

    # Read the encrypted file
    with open(encrypted_file_path, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Decrypt the data
    decrypted_data = fernet.decrypt(encrypted_data)

    # Save the decrypted file
    with open(restore_path, "wb") as restored_file:
        restored_file.write(decrypted_data)

    print(f"File decrypted and restored to {restore_path}")

decrypt_file(r"C:\Guardium\Quarantine\1ea3dc626b9ccee026502ac8e8a98643c65a055829e8d8b1750b2468254c0ab1.enc", r"D:\Viruses\1ea3dc626b9ccee026502ac8e8a98643c65a055829e8d8b1750b2468254c0ab1")