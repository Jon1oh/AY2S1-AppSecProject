class Cars:

    def __init__(self, car_model, car_brand, car_price):
        self.__car_id = 0
        self.__car_model = car_model
        self.__car_brand = car_brand
        self.__car_price = car_price


    def get_car_id(self):
        return self.__car_id

    def get_car_model(self):
        return self.__car_model

    def get_car_brand(self):
        return self.__car_brand

    def get_car_price(self):
        return self.__car_price

    def set_car_id(self, car_id):
        self.__car_id = car_id

    def set_car_model(self, car_model):
        self.__car_model = car_model

    def set_car_brand(self, car_brand):
        self.__car_brand = car_brand

    def set_car_price(self, car_price):
        self.__car_price = car_price


