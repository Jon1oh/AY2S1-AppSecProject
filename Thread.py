class Thread:

    def __init__(self, thread_username, thread_title, thread_message, thread_reply):
        self.__thread_id = 1
        self.__thread_username = thread_username
        self.__thread_title = thread_title
        self.__thread_message = thread_message
        self.__thread_reply = thread_reply

    def get_thread_id(self):
        return self.__thread_id

    def get_thread_username(self):
        return self.__thread_username

    def get_thread_title(self):
        return self.__thread_title

    def get_thread_message(self):
        return self.__thread_message

    def get_thread_reply(self):
        return self.__thread_reply

    def set_thread_id(self, thread_id):
        self.__thread_id = thread_id

    def set_thread_username(self, thread_username):
        self.__thread_username = thread_username

    def set_thread_title(self, thread_title):
        self.__thread_title = thread_title

    def set_thread_message(self, thread_message):
        self.__thread_message = thread_message

    def set_thread_reply(self, thread_reply):
        self.__thread_reply = thread_reply