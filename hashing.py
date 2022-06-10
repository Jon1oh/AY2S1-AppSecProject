import bcrypt

def hashing(password, confirm_password):
    encoded_pw = password.encode()
    encoded_cfm_pw = confirm_password.encode()
    
    #hash the encoded password
    hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt())    
    hashed_cfm_pw = bcrypt.hashpw(encoded_cfm_pw, bcrypt.gensalt())

    # store data in shelve database
    # write the hash of the password to file
    with open('hash.key', 'a+') as file:
        # move cursor to start of file
        file.seek(0)
        # check if file contains data
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write(str(hashed_pw)) # hashed_pw is the digest of the hashed password
        file.write(str(hashed_cfm_pw)) # hashed_cfm_pw is the digest of the confirmed password
