from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes
import zlib
import binascii
import random


def generate_keypair(bits=2048):
    e = 65537
    p = getPrime(bits // 2)
    q = getPrime(bits // 2)
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

def pad(data, block_size):
    padding_length = block_size - len(data)
    padding = bytes([padding_length]) * padding_length
    return data + padding

def unpad(data):
    padding_length = data[-1]
    return data[:-padding_length]

def ecb_encrypt_data(data, pub_key):
    # -1 not working
    block_size = ((pub_key[1].bit_length()+7)// 8) - 1
    print("text block size BE:", block_size)
    print("data length:", len(data))
    encrypted_data = []
    lenght_of_last_block = int()
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        lenght_of_last_block = len(block)
        # if len(block) < block_size:
        #     block = unpad(block)
        encrypted_block = rsa_encrypt(bytes_to_long(block), pub_key)
        encrypted_data.append(long_to_bytes(encrypted_block, (pub_key[1].bit_length()+7)// 8))

    print("encryption block size:", (pub_key[1].bit_length()+7)// 8)
    return b''.join(encrypted_data)

def ecb_decrypt_data(data, priv_key):
    block_size = (priv_key[1].bit_length()+7)// 8
    print("decryption block size:", block_size)
    print("data length:", len(data))
    decrypted_data = []
    index_block = 1
    for i in range(0, len(data), block_size):
        last_iteration = len(data)/block_size
        block = data[i:i + block_size]
        decrypted_block = rsa_decrypt(bytes_to_long(block), priv_key)
        if (index_block != last_iteration):

            decrypted_data.append(long_to_bytes(decrypted_block,((priv_key[1].bit_length()+7)// 8)-1))
        else:

            lenght_of_last_block = len(long_to_bytes(decrypted_block))
            print("LAST block: length: ", lenght_of_last_block)
            decrypted_data.append(long_to_bytes(decrypted_block, lenght_of_last_block))

        index_block=index_block+1

    print("text block size AD:", ((priv_key[1].bit_length()+7)// 8)-1)
    joined = b''.join(decrypted_data)
    print("Final data length", len(joined))
    return joined

def cbc_encrypt_data(data, pub_key):
    # -1 not working
    block_size = ((pub_key[1].bit_length()+7)// 8) - 1
    print("text block size BE:", block_size)
    print("data length:", len(data))
    encrypted_data = []
    lenght_of_last_block = int()

    IV = random.getrandbits(pub_key[1].bit_length())
    prev = IV
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        lenght_of_last_block = len(block)

        prev = prev.to_bytes(pub_key[1].bit_length(),'big')
        prev = bytes_to_long(prev[:len(block)])
        xor = bytes_to_long(block) ^ prev

        encrypted_block = rsa_encrypt(xor, pub_key)
        encrypted_data.append(long_to_bytes(encrypted_block, (pub_key[1].bit_length()+7)// 8))
        prev = encrypted_block
    print("encryption block size:", (pub_key[1].bit_length()+7)// 8)
    return b''.join(encrypted_data), IV

def cbc_decrypt_data(data, priv_key,IV):
    block_size = (priv_key[1].bit_length()+7)// 8
    print("decryption block size:", block_size)
    print("data length:", len(data))
    decrypted_data = []
    index_block = 1

    prev = IV
    for i in range(0, len(data), block_size):
        last_iteration = len(data)/block_size
        block = data[i:i + block_size]
        decrypted_block = rsa_decrypt(bytes_to_long(block), priv_key)
        lenght_of_last_block = len(long_to_bytes(decrypted_block))

        prev = prev.to_bytes(priv_key[1].bit_length(),'big')
        prev = bytes_to_long(prev[:lenght_of_last_block])
        xor = decrypted_block ^ prev
        prev = bytes_to_long(block)



        if (index_block != last_iteration):

            decrypted_data.append(long_to_bytes(xor,((priv_key[1].bit_length()+7)// 8)-1))
        else:
            print("LAST block: length: ", lenght_of_last_block)
            decrypted_data.append(long_to_bytes(xor, lenght_of_last_block))

        index_block=index_block+1



    print("text block size AD:", ((priv_key[1].bit_length()+7)// 8)-1)
    joined = b''.join(decrypted_data)
    print("Final data length", len(joined))
    return joined
def calculate_crc(chunk_type, chunk_data):

    return binascii.crc32(chunk_type + chunk_data) & 0xffffffff


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
        idat_data = b''
        skip = 0
        IV = 0
        #concatenate all idat data
        while True:

            chunk_length_encoded = infile.read(4)
            if len(chunk_length_encoded) < 4:
                break  # End of file reached

            chunk_length = int.from_bytes(chunk_length_encoded, byteorder='big')
            chunk_type = infile.read(4)
            chunk_data = infile.read(chunk_length)
            chunk_crc = infile.read(4)
            chunk_type_decoded = chunk_type.decode('ascii')
            # Check if chunk is IDAT, if its IDAT encode it
            if chunk_type == b'IDAT':
                print(f"IDAT CHUNK, contatenating:")
                idat_data += chunk_data

        infile.seek(8)
        print("seek")
        while True:
            chunk_length_encoded = infile.read(4)
            if len(chunk_length_encoded) < 4:
                break  # End of file reached


            chunk_length = int.from_bytes(chunk_length_encoded, byteorder='big')
            chunk_type = infile.read(4)
            chunk_data = infile.read(chunk_length)
            chunk_crc = infile.read(4)
            chunk_type_decoded = chunk_type.decode('ascii')
            # Check if chunk is IDAT, if its IDAT encode it

            if chunk_type == b'IDAT':
                print("IDAT")
                if skip == 0:
                    print(f"IDAT CHUNK, ENCRYPTING:")
                    if compressed == 1:
                        if method == 0:
                            encrypted_data = ecb_encrypt_data(idat_data, pub_key)
                        else:
                            encrypted_data,IV = cbc_encrypt_data(idat_data, pub_key)
                    else:

                        decompressed = zlib.decompress(idat_data)
                        if method == 0:
                            encrypted_data = ecb_encrypt_data(decompressed, pub_key)
                        else:
                            encrypted_data,IV = cbc_encrypt_data(decompressed, pub_key)
                        encrypted_data = zlib.compress(encrypted_data)


                    # Split the encrypted data back into IDAT chunks
                    max_chunk_size = 8192  # PNG standard maximum chunk size
                    for i in range(0, len(encrypted_data), max_chunk_size):
                        chunk = encrypted_data[i:i + max_chunk_size]
                        chunk_length_encoded = len(chunk).to_bytes(4, byteorder='big')
                        chunk_crc = calculate_crc(b'IDAT', chunk).to_bytes(4, byteorder='big')
                        outfile.write(chunk_length_encoded)
                        outfile.write(b'IDAT')
                        outfile.write(chunk)
                        outfile.write(chunk_crc)

                    skip = 1
            else:
                print(f"NOT IDAT, NOT ENCRYPTED:")
                # Write the chunk length, type, data, and CRC to the output file
                outfile.write(chunk_length_encoded)
                outfile.write(chunk_type)
                outfile.write(chunk_data)
                outfile.write(chunk_crc)

    # Read the modified file and return its bytes
    with open(output_path, 'rb') as file:
        encrypted_png_data = file.read()

    return encrypted_png_data,IV

def png_decryption(file_path, priv_key,method=0,compressed=1,IV=0):
    output_path = file_path.replace('.png', 'decryption.png')

    with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
        # Copy the PNG signature
        header = infile.read(8)
        if header != b'\x89PNG\r\n\x1a\n':
            raise ValueError("File is not a valid PNG")
        outfile.write(header)
        idat_data = b''
        skip = 0
        # concatenate all idat data
        while True:

            chunk_length_encoded = infile.read(4)
            if len(chunk_length_encoded) < 4:
                break  # End of file reached

            chunk_length = int.from_bytes(chunk_length_encoded, byteorder='big')
            chunk_type = infile.read(4)
            chunk_data = infile.read(chunk_length)
            chunk_crc = infile.read(4)
            chunk_type_decoded = chunk_type.decode('ascii')
            if chunk_type == b'IDAT':
                print(f"IDAT CHUNK, contatenating:")
                idat_data += chunk_data

        infile.seek(8)
        while True:
            chunk_length_encoded = infile.read(4)
            if len(chunk_length_encoded) < 4:
                break  # End of file reached

            chunk_length = int.from_bytes(chunk_length_encoded, byteorder='big')
            chunk_type = infile.read(4)
            chunk_data = infile.read(chunk_length)
            chunk_crc = infile.read(4)
            chunk_type_decoded = chunk_type.decode('ascii')
            # Check if chunk is IDAT, if its IDAT decode it
            if chunk_type == b'IDAT':
                if skip == 0:
                    print(f"IDAT CHUNK, DECRYPTING:")
                    if compressed == 1:
                        if method == 0:
                            decrypted_data = ecb_decrypt_data(idat_data, priv_key)
                        else:
                            decrypted_data = cbc_decrypt_data(idat_data, priv_key,IV)
                    else:

                        decompressed = zlib.decompress(idat_data)
                        if method == 0:
                            decrypted_data = ecb_decrypt_data(decompressed, priv_key)
                        else:
                            decrypted_data = cbc_decrypt_data(decompressed, priv_key,IV)
                        decrypted_data = zlib.compress(decrypted_data)
                    # Split the encrypted data back into IDAT chunks
                    max_chunk_size = 8192  # PNG standard maximum chunk size
                    for i in range(0, len(decrypted_data), max_chunk_size):
                        chunk = decrypted_data[i:i + max_chunk_size]
                        chunk_length_encoded = len(chunk).to_bytes(4, byteorder='big')
                        chunk_crc = calculate_crc(b'IDAT', chunk).to_bytes(4, byteorder='big')
                        outfile.write(chunk_length_encoded)
                        outfile.write(b'IDAT')
                        outfile.write(chunk)
                        outfile.write(chunk_crc)

                    skip = 1

            else:
                print(f"NOT IDAT, NOT DECRYPTED:")
                # Write the chunk length, type, data, and CRC to the output file
                outfile.write(chunk_length_encoded)
                outfile.write(chunk_type)
                outfile.write(chunk_data)
                outfile.write(chunk_crc)

    # Read the modified file and return its bytes
    with open(output_path, 'rb') as file:
        decrypted_png_data = file.read()

    return decrypted_png_data

