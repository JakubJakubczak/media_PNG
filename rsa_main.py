from rsa import*

image = "penguin.png"

pub_key, priv_key = generate_keypair()

png_encryption(image,pub_key,0,1)
png_decryption(image.replace('.png', 'encryption.png'),priv_key,0,1)

print("Koniec")




# padding
# zdebugować, żeby działało zawsze a nie losowo 255/256
# dla penguin nie dziala zdekompersowane


# inna metoda szyfrowania oprocz ecb
# szyfrowac gotowa funkcja rsa