def get_png_header(file_path):
    with open(file_path, "rb") as file:
        # reading first 8 bytes
            header = file.read(8)
            if not header:
                print("End of file reached or unable to read byte.")

    header_hex = ' '.join(format(byte, '02X') for byte in header)
    return header_hex

# add chunk type as parameter
def read_chunk(file_path, chunk_name):
    chunk_bytes = chunk_name.encode('ascii')

    with open(file_path, 'rb') as file:
        # Check PNG header
        header = file.read(8)
        if header != b'\x89PNG\r\n\x1a\n':
            raise ValueError("File is not a valid PNG")

        # Search for chunk
        while True:
            length = file.read(4)
            if len(length) == 0:
                print("Reached end of file")
                return None
            chunk_length = int.from_bytes(length, byteorder='big')
           # if chunk_length < 4:
            #    return None #end of file
            chunk_type = file.read(4)
            if chunk_type == chunk_bytes:
                break
            else:
                file.seek(chunk_length + 4, 1)
                    #return 0 # end of file

        # Read chunk
        chunk_data = file.read(chunk_length)

        # Change to hex
        chunk_hex = ' '.join(format(byte, '02X') for byte in  chunk_data)
    return chunk_hex

#Reading chunk when multiple instances occur

def read_chunks(file_path, chunk_name):
    chunk_bytes = chunk_name.encode('ascii')

    with open(file_path, 'rb') as file:
        # Check PNG header
        header = file.read(8)
        if header != b'\x89PNG\r\n\x1a\n':
            raise ValueError("File is not a valid PNG")
        chunk_concatenated = b""
        # Search for chunks
        while True:
            chunk_length = int.from_bytes(file.read(4), byteorder='big')
            chunk_type = file.read(4)
            if chunk_type == chunk_bytes:
                # Read chunk
                chunk_data = file.read(chunk_length)
                chunk_concatenated += chunk_data
                file.seek(4, 1) # skip control sum
                continue
            elif chunk_type == b'IEND':
                break
            else:
                file.seek(chunk_length + 4, 1)
                    #return 0 # end of file



        # Change to hex
        chunk_hex = ' '.join(format(byte, '02X') for byte in  chunk_concatenated)
    return chunk_hex

#Anonimization
#Deleting chunks that starts with lower letter

def delete_chunks_with_lower_letter(file_path):
    output_path = file_path.replace('.png', '_modified.png')

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
            # Check if the first letter of the chunk type is lowercase
            if chunk_type_decoded[0].islower():
                print(f"Skipping chunk: {chunk_type_decoded}")
                # Skip the chunk data and CRC
                infile.seek(chunk_length + 4, 1)
            else:
                print(f"Keeping chunk: {chunk_type_decoded}")
                chunk_data = infile.read(chunk_length)
                chunk_crc = infile.read(4)
                # Write the chunk length, type, data, and CRC to the output file
                outfile.write(chunk_length_encoded)
                outfile.write(chunk_type)
                outfile.write(chunk_data)
                outfile.write(chunk_crc)

    # Read the modified file and return its bytes
    with open(output_path, 'rb') as file:
        modified_png_data = file.read()

    return modified_png_data