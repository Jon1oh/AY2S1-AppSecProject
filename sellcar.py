class Sellcar:

    def __init__(self, car_model, car_brand, car_price, condition, remarks):
        self.__sellcar_id = 0
        self.__car_model = car_model
        self.__car_brand = car_brand
        self.__car_price = car_price
        self.__condition = condition
        self.__remarks = remarks

    def get_sellcar_id(self):
        return self.__sellcar_id

    def get_car_model(self):
        return self.__car_model

    def get_car_brand(self):
        return self.__car_brand

    def get_car_price(self):
        return self.__car_price

    def get_condition(self):
        return self.__condition

    def get_remarks(self):
        return self.__remarks

    def set_sellcar_id(self, sellcar_id):
        self.__sellcar_id = sellcar_id

    def set_car_model(self, car_model):
        self.__car_model = car_model

    def set_car_brand(self, car_brand):
        self.__car_model = car_brand

    def set_car_price(self, car_price):
        self.__car_price = car_price

    def set_condition(self, condition):
        self.__condition = condition

    def set_remarks(self, remarks):
        self.__remarks = remarks

