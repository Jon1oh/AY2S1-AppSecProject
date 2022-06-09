import rsa
import bcrypt

def asymEncrypt(message):
    encoded = message.encode()
    
    #hash the encoded password
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())    

    # generate the public and private keys
    public, private = rsa.newkeys(512) # 512 bit keys
    
    # encrypt the plaintext
    encrypted = rsa.encrypt(encoded, public) # encrypt the encoded mesage using publiv key

    decrypted = rsa.decrypt(encrypted, private).decode()

    print(hashed)
    print(public, private)
    print(encrypted)
    print(decrypted)

    # store data in shleve database
    # write the hash of the password to file
    with open('hash.key', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(hashed))

    # write the ciphertext to file
    with open('ciphertext.txt', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(encrypted))

    # write the key to the file
    with open('key.key', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(public))
        file.write(str(private))