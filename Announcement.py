from Thread import Thread


class Announcement(Thread):

    def __init__(self, thread_username, thread_title, thread_message, thread_reply, announcement_type, severity_level):
        super().__init__(thread_username, thread_title, thread_message, thread_reply)
        self.__announcement_id = 1
        self.__announcement_type = announcement_type
        self.__severity_level = severity_level

    def get_announcement_id(self):
        return self.__announcement_id

    def get_announcement_type(self):
        return self.__announcement_type

    def get_severity_level(self):
        return self.__severity_level

    def set_announcement_id(self, announcement_id):
        self.__announcement_id = announcement_id

    def set_announcement_type(self, announcement_type):
        self.__announcement_type = announcement_type

    def set_severity_level(self, severity_level):
        self.__severity_level = severity_level
