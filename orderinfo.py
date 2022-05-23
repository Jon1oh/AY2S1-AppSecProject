import Order


class orderinfo(Order.Order):
    count_id = 0

    def __init__(self, address, postal_code, model, price, date):
        super().__init__(address, postal_code)
        orderinfo.count_id += 1
        self.__orderinfo_id = orderinfo.count_id
        self.__model = model
        self.__price = price
        self.__date = date

    def get_orderinfo_id(self):
        return self.__orderinfo_id

    def get_model(self):
        return self.__model

    def get_price(self):
        return self.__price

    def get_postal_date(self):
        return self.__date

    def set_orderinfo_id(self, orderinfo_id):
        self.__orderinfo_id = orderinfo_id

    def set_model(self, model):
        self.__model = model

    def set_price(self, price):
        self.__price = price

    def set_date(self, date):
        self.__date = date
