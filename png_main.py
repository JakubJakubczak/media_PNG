import cv2
import sys # to access the system
import numpy as np
import matplotlib.pyplot as plt
import zlib
from png import*

image = "queen.png"
header = get_png_header(image)

print("Header:")
print(header)

chunk_text = read_chunk(image,"IHDR")
if chunk_text !=0:
    print("IHDR BYTES::")
    print(chunk_text)

    bytes_list = chunk_text.split(' ')

    #IHDR DATA

    width = int(''.join(bytes_list[:4]),16)
    height = int(''.join(bytes_list[4:8]),16)
    bitdepth = int(''.join(bytes_list[8]),16)
    color_type = int(''.join(bytes_list[9]),16)
    compression_method = int(''.join(bytes_list[10]),16)
    filter_type = int(''.join(bytes_list[11]),16)
    interlace_method = int(''.join(bytes_list[12]),16)

    print("IHDR DATA DECODED:")
    print("Width:", width)
    print("Height:", height)
    print("Bit Depth:", bitdepth)
    print("Color Type:", color_type)
    print("Compression Method:", compression_method)
    print("Filter Type:", filter_type)
    print("Interlace Method:", interlace_method)
else:
    print("IHDR chunk not found, error")

#IDAT

chunk_text = read_chunks(image,"IDAT") # HEX
bytes_chunk_text = bytes.fromhex(chunk_text)

decompressed_IDAT_DATA = zlib.decompress(bytes_chunk_text)
rgba_IDAT_DATA = [int.from_bytes(decompressed_IDAT_DATA[i:i+1], 'big') for i in range(len(decompressed_IDAT_DATA))]

# filter?
print("IDAT BYTES:")
print("IDAT decompressed length:", len(decompressed_IDAT_DATA))
print(rgba_IDAT_DATA[0:12])

#IEND
print("IEND:")
chunk_text = read_chunk(image,"IEND")
print(chunk_text)

#PLTE
print("PLTE")
chunk_text = read_chunk(image,"PLTE")
if chunk_text:
    print(chunk_text)

#bKGD
print("bKGD BYTES:")
chunk_text = read_chunk(image,"bKGD")
if chunk_text:
    print(chunk_text)
#cHRM
print("cHRM BYTES:")
chunk_text = read_chunk(image,"cHRM")
if chunk_text:
    print(chunk_text)
    bytes_list = chunk_text.split(' ')

    #cHRM DATA

    white_point_x = int(''.join(bytes_list[:4]),16) /100000
    white_point_y = int(''.join(bytes_list[4:8]),16) /100000
    red_x = int(''.join(bytes_list[8:12]),16) /100000
    red_y = int(''.join(bytes_list[12:16]),16) /100000
    green_x = int(''.join(bytes_list[16:20]),16) /100000
    green_y = int(''.join(bytes_list[20:24]),16) /100000
    blue_x = int(''.join(bytes_list[24:28]),16) /100000
    blue_y = int(''.join(bytes_list[28:32]),16) /100000

    print("cHRM DATA DECODED:")
    print("white point x:", white_point_x)
    print("White point y:", white_point_y)
    print("Red x:", red_x)
    print("Red y:", red_y)
    print("Green x:", green_x)
    print("Green y:", green_y)
    print("blue x:", blue_x)
    print("blue y:", blue_y)
else:
    print("cHRM chunk not found")

#gAMA
print("gAMA BYTES:")
chunk_text = read_chunk(image,"gAMA")
if chunk_text:
    print(chunk_text)
    bytes_list = chunk_text.split(' ')

    #cHRM DATA

    gamma = int(''.join(bytes_list[:4]),16) /100000
    print("gAMA DATA DECODED:")
    print("Gamma:", gamma)
else:
    print("gAMA chunk not found")

#Fourier's transformation and visualisation
# Read the PNG file
image_fourier = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

# Apply Fourier Transform
f_transform = np.fft.fft2(image_fourier)
f_transform_shifted = np.fft.fftshift(f_transform)

# Compute magnitude spectrum
magnitude_spectrum = 20 * np.log(np.abs(f_transform_shifted))

# Display the transformed image
plt.imshow(magnitude_spectrum, cmap='gray')
plt.title('Fourier Transform Magnitude Spectrum')
plt.colorbar()
plt.show()

#Anonimization
# Anonymize the PNG file by deleting chunks with lowercase first letters
modified_png_bytes = delete_chunks_with_lower_letter(image)

image_modified = image.replace('.png', '_modified.png')
# Open the image file using PIL
img = cv2.imread(image_modified, cv2.IMREAD_ANYCOLOR)

while True:
    cv2.imshow("image", img)
    cv2.waitKey(0)
    sys.exit()  # to exit from all the processes

# cv2.destroyAllWindows()  # destroy all windows
