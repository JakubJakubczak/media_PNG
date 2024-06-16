from rsa_c import*

image = "queen.png"

pub_key, priv_key = generate_keypair()
pub_rsa, priv_rsa = generate_rsa_keypair()

compression = 1
method = 1

data,IV = png_encryption(image,pub_key,method,compression)
data2,IV2 = png_rsa_encryption(image,pub_rsa,method,compression)
png_decryption(image.replace('.png', 'encryption.png'),priv_key,method,compression,IV)
png_rsa_decryption(image.replace('.png', 'rsa_encryption.png'),priv_rsa,method,compression,IV2)
print("Koniec")




# padding - ZROBIONE!!!
# zdebugować, żeby działało zawsze a nie losowo 255/256 - ZROBIONE!!!
# nie działa dla wielu chunkow IDAT, problem z ostatnim blokiem - ZROBIONE!!!
# dla penguin nie dziala zdekompersowane  - ZROBIONE!!!

# inna metoda szyfrowania oprocz ecb
# szyfrowac gotowa funkcja rsa ZROBIONE!!!