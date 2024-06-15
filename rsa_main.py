from rsa import*

image = "sample.png"

pub_key, priv_key = generate_keypair()

compression = 1
method = 0
png_encryption(image,pub_key,method,compression )
png_decryption(image.replace('.png', 'encryption.png'),priv_key,method,compression)

print("Koniec")




# padding - ZROBIONE!!!
# zdebugować, żeby działało zawsze a nie losowo 255/256 - ZROBIONE!!!
# nie działa dla wielu chunkow IDAT, problem z ostatnim blokiem - ZROBIONE!!!

# dla penguin nie dziala zdekompersowane
# inna metoda szyfrowania oprocz ecb
# szyfrowac gotowa funkcja rsa