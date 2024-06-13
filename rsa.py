from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes
import zlib

def generate_keypair(bits=2048):
    e = 65537
    p = getPrime(bits // 2)
    q = getPrime(bits // 2)
    print(p,q)
    n = p * q
    phi = (p - 1) * (q - 1)
    d = inverse(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(m, pub_key):
    e, n = pub_key
    return pow(m, e, n)

def rsa_decrypt(c, priv_key):
    d, n = priv_key
    return pow(c, d, n)

def ecb_encrypt_data(data, pub_key):
    block_size = (pub_key[1].bit_length()// 8) -1
    print("encryption block size:", block_size)
    encrypted_data = []
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        encrypted_block = rsa_encrypt(bytes_to_long(block), pub_key)
        encrypted_data.append(long_to_bytes(encrypted_block, block_size + 1))
    return b''.join(encrypted_data)

def ecb_decrypt_data(data, priv_key):
    block_size = (priv_key[1].bit_length()// 8)
    print("decryption block size:", block_size)
    decrypted_data = []
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        decrypted_block = rsa_decrypt(bytes_to_long(block), priv_key)
        decrypted_data.append(long_to_bytes(decrypted_block, block_size - 1))
    return b''.join(decrypted_data)

#method argument for chosing method of encryption, deafult 0 - ecb
#compresed - whether IDAT data is compressed when encrypting
def png_encryption(file_path, pub_key, method=0,compressed=1):
    output_path = file_path.replace('.png', 'encryption.png')


    with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
        # Copy the PNG signature
        header = infile.read(8)
        if header != b'\x89PNG\r\n\x1a\n':
            raise ValueError("File is not a valid PNG")
        outfile.write(header)

        while True:

            chunk_length_encoded = infile.read(4)
            if len(chunk_length_encoded) < 4:
                break  # End of file reached

            chunk_length = int.from_bytes(chunk_length_encoded, byteorder='big')
            chunk_type = infile.read(4)
            chunk_type_decoded = chunk_type.decode('ascii')
            # Check if chunk is IDAT, if its IDAT encode it
            if chunk_type_decoded == 'IDAT':
                print(f"IDAT CHUNK, ENCODING:")
                chunk_data = infile.read(chunk_length)
                if compressed == 1:
                    encrypted_data = ecb_encrypt_data(chunk_data,pub_key)
                else:
                    decompressed = zlib.decompress(chunk_data)
                    encrypted_data = ecb_encrypt_data(decompressed ,pub_key)
                    encrypted_data = zlib.compress(encrypted_data)

                encrypted_length_encoded = len(encrypted_data).to_bytes(4, byteorder='big')
                chunk_crc = infile.read(4) # skipping crc
                outfile.write(encrypted_length_encoded)
                outfile.write(chunk_type)
                outfile.write(encrypted_data)
                outfile.write(chunk_crc)
            else:
                print(f"NOT IDAT, NOT ENCODED:")
                chunk_data = infile.read(chunk_length)
                chunk_crc = infile.read(4)
                # Write the chunk length, type, data, and CRC to the output file
                outfile.write(chunk_length_encoded)
                outfile.write(chunk_type)
                outfile.write(chunk_data)
                outfile.write(chunk_crc)

    # Read the modified file and return its bytes
    with open(output_path, 'rb') as file:
        encrypted_png_data = file.read()

    return encrypted_png_data

def png_decryption(file_path, priv_key,method=0,compressed=1):
    output_path = file_path.replace('.png', 'decryption.png')

    with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
        # Copy the PNG signature
        header = infile.read(8)
        if header != b'\x89PNG\r\n\x1a\n':
            raise ValueError("File is not a valid PNG")
        outfile.write(header)

        while True:

            chunk_length_encoded = infile.read(4)
            if len(chunk_length_encoded) < 4:
                break  # End of file reached

            chunk_length = int.from_bytes(chunk_length_encoded, byteorder='big')
            chunk_type = infile.read(4)
            chunk_type_decoded = chunk_type.decode('ascii')
            # Check if chunk is IDAT, if its IDAT decode it
            if chunk_type_decoded == 'IDAT':
                print(f"IDAT CHUNK, Decoding:")
                chunk_data = infile.read(chunk_length)
                if compressed == 1:
                    decrypted_data = ecb_decrypt_data(chunk_data,priv_key)
                else:
                    decompressed = zlib.decompress(chunk_data)
                    decrypted_data = ecb_decrypt_data(decompressed, priv_key)
                    decrypted_data = zlib.compress(decrypted_data)

                decrypted_length_encoded = len(decrypted_data).to_bytes(4, byteorder='big')
                chunk_crc = infile.read(4) # skipping crc
                outfile.write(decrypted_length_encoded)
                outfile.write(chunk_type)
                outfile.write(decrypted_data)
                outfile.write(chunk_crc)
            else:
                print(f"NOT IDAT, skipping:")
                chunk_data = infile.read(chunk_length)
                chunk_crc = infile.read(4)
                # Write the chunk length, type, data, and CRC to the output file
                outfile.write(chunk_length_encoded)
                outfile.write(chunk_type)
                outfile.write(chunk_data)
                outfile.write(chunk_crc)

    # Read the modified file and return its bytes
    with open(output_path, 'rb') as file:
        decrypted_png_data = file.read()

    return decrypted_png_data

