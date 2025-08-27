import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

KEY_SIZE = 32
KEYS_DIR = os.path.join(os.path.dirname(__file__), '..', 'keys')

def generate_and_save_key(filename):
    
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)
        
    key = get_random_bytes(KEY_SIZE)
    key_path = os.path.join(KEYS_DIR, f"{filename}.key")
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    return key

def load_key(filename):
    
    key_path = os.path.join(KEYS_DIR, f"{filename}.key")
    try:
        with open(key_path, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        return None

def encrypt_file(input_path, output_path, key):
    
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(input_path, "rb") as f_in:
        padded_data = pad(f_in.read(), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)

    with open(output_path, "wb") as f_out:
        f_out.write(iv + encrypted_data)

def decrypt_file_data(input_path, key):
    
    with open(input_path, "rb") as f_in:
        
        iv = f_in.read(AES.block_size)
        encrypted_data = f_in.read()


    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded_data = cipher.decrypt(encrypted_data)


    original_data = unpad(decrypted_padded_data, AES.block_size)
    return original_data