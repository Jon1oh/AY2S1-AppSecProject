# Edited to change file name
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, full_name, gender, email, mobile_no, address, postal_code, username, password, confirm_password, member):
        self.__user_id = 1
        self.__full_name = full_name
        self.__gender = gender
        self.__email = email
        self.__mobile_no = mobile_no
        self.__address = address
        self.__postal_code = postal_code
        self.__username = username
        self.__password = password
        self.__confirm_password = confirm_password
        self.__member = member

    def get_id(self):
        return self.__user_id

    def get_member(self):
        return self.__member

    def get_user_id(self):
        return self.__user_id

    def get_full_name(self):
        return self.__full_name

    def get_gender(self):
        return self.__gender

    def get_email(self):
        return self.__email

    def get_mobile_no(self):
        return self.__mobile_no

    def get_address(self):
        return self.__address

    def get_postal_code(self):
        return self.__postal_code

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_confirm_password(self):
        return self.__confirm_password

    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_full_name(self, full_name):
        self.__full_name = full_name

    def set_gender(self, gender):
        self.__gender = gender

    def set_email(self, email):
        self.__email = email

    def set_mobile_no(self, mobile_no):
        self.__mobile_no = mobile_no

    def set_address(self, address):
        self.__address = address

    def set_postal_code(self, postal_code):
        self.__postal_code = postal_code

    def set_username(self, username):
        self.__username = username

    def set_password(self, password):
        self.__password = password

    def set_member(self, member):
        self.__member = member

    def set_confirm_password(self, confirm_password):
        self.__confirm_password = confirm_password
