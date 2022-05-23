class Order:
    count_id=0

    def __init__(self, address, postal_code, card_name, card_no, expmonth, expyear, cvv):
        Order.count_id += 1
        self.__order_id = Order.count_id
        self.__address = address
        self.__postal_code = postal_code
        self.__card_name = card_name
        self.__card_no = card_no
        self.__expmonth = expmonth
        self.__expyear = expyear
        self.__cvv = cvv

    def get_order_id(self):
        return self.__order_id

    def get_address(self):
        return self.__address

    def get_postal_code(self):
        return self.__postal_code

    def get_card_name(self):
        return self.__card_name

    def get_card_no(self):
        return self.__card_no

    def get_expmonth(self):
        return self.__expmonth

    def get_expyear(self):
        return self.__expyear

    def get_cvv(self):
        return self.__cvv

    def set_order_id(self, order_id):
        self.__order_id = order_id

    def set_address(self, address):
        self.__address = address

    def set_postal_code(self, postal_code):
        self.__postal_code = postal_code

    def set_card_name(self, card_name):
        self.__card_name = card_name

    def set_card_no(self, card_no):
        self.__card_no = card_no

    def set_expmonth(self, expmonth):
        self.__expmonth = expmonth

    def set_expyear(self, expyear):
        self.__expyear = expyear

    def set_cvv(self, cvv):
        self.__cvv = cvv
