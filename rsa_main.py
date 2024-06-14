from rsa import*

image = "mario.png"

pub_key, priv_key = generate_keypair()

compression = 0
png_encryption(image,pub_key,0,compression )
png_decryption(image.replace('.png', 'encryption.png'),priv_key,0,compression)

print("Koniec")




# padding
# zdebugować, żeby działało zawsze a nie losowo 255/256
# dla penguin nie dziala zdekompersowane


# inna metoda szyfrowania oprocz ecb
# szyfrowac gotowa funkcja rsa