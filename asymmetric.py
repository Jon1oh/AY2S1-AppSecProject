import rsa
import bcrypt

def asymEncrypt(password):
    encoded = password.encode()
    
    #hash the encoded password
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())    

    # generate the public and private keys
    public, private = rsa.newkeys(512) # 512 bit keys
    
    # encrypt the plaintext
    encrypted = rsa.encrypt(encoded, public) # encrypt the encoded message using public key

    decrypted = rsa.decrypt(encrypted, private).decode()

    # store data in shelve database
    # write the hash of the password to file
    with open('hash.key', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(hashed)) # hashed is the digest of the hashed password

    # write the cipher-text to file
    with open('ciphertext.txt', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(encrypted)) # cipher-text of password

    # write the key to the file
    with open('key.key', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(public)) # public key
        file.write(str(private)) # private key