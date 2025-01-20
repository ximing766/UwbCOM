from Crypto.Cipher import DES, DES3
from Crypto.Util.Padding import pad, unpad

class MyEcbDes:
    def __init__(self, key):
        self.key = bytes.fromhex(key)

    def des_encrypt(self, plaintext):
        cipher = DES.new(self.key, DES.MODE_ECB)
        padded_plaintext = pad(bytes.fromhex(plaintext), DES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        return ciphertext.hex()

    def des_decrypt(self, ciphertext):
        cipher = DES.new(self.key, DES.MODE_ECB)
        padded_plaintext = cipher.decrypt(bytes.fromhex(ciphertext))
        plaintext = unpad(padded_plaintext, DES.block_size)
        return plaintext.hex()

    def des3_encrypt(self, plaintext):
        cipher = DES3.new(self.key, DES3.MODE_ECB)
        padded_text = pad(bytes.fromhex(plaintext), DES3.block_size)
        return cipher.encrypt(padded_text).hex()

    def des3_decrypt(self, ciphertext):
        cipher = DES3.new(self.key, DES3.MODE_ECB)
        decrypted_padded_text = cipher.decrypt(bytes.fromhex(ciphertext))
        return unpad(decrypted_padded_text, DES3.block_size).hex()

if __name__ == '__main__':
    key = 'B6E6AB003A9455A3'
    plaintext = 'F9350143053F0001'
    crypto_helper = MyEcbDes(key)

    ciphertext = crypto_helper.des_encrypt(plaintext)
    print(f"Ciphertext: {ciphertext}")
    decrypted_text = crypto_helper.des_decrypt(ciphertext)
    print(f"Decrypted text: {decrypted_text}")

    plaintext = 'F9350143053F0001'
    crypto_helper.key = bytes.fromhex('B6E6AB003A9455A33DBE8869ECC59BE9')

    ciphertext = crypto_helper.des3_encrypt(plaintext)
    print(f"Ciphertext: {ciphertext}")
    decrypted_text = crypto_helper.des3_decrypt(ciphertext)
    print(f"Decrypted text: {decrypted_text}")