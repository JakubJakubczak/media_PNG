from Crypto.Util import number

def generate_keypair(bits):
    p = number.getPrime(bits)
    q = number.getPrime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)
    return ((e, n), (d, n))

def rsa_encrypt(plaintext, public_key):
    e, n = public_key
    ciphertext = [pow(byte, e, n) for byte in plaintext]
    return ciphertext

def rsa_decrypt(ciphertext, private_key):
    d, n = private_key
    plaintext = [pow(byte, d, n) for byte in ciphertext]
    return plaintext

def ecb_encrypt(data, public_key):
    block_size = 1
    encrypted_data = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        encrypted_block = rsa_encrypt(block, public_key)
        encrypted_data.extend(bytearray(encrypted_block))
    return encrypted_data

def ecb_decrypt(data, private_key):
    block_size = 1
    decrypted_data = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        decrypted_block = rsa_decrypt(block, private_key)
        decrypted_data.extend(bytearray(decrypted_block))
    return decrypted_data