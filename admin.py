# Changed file name

import User


class Admin(User.User):
    def __init__(self, code):
        super().__init__("Jordan", "Male", "admin@email.com", "12345678", None, None, "Admin", 1234, 1234)
        self.__code = code
        self.__user_id = 1

    def set_code(self, value):
        self.__code = value

    def get_code(self):
        return self.__code

    def get_user_id(self):
        return self.__user_id

    def set_user_id(self, user_id):
        self.__user_id = user_id
