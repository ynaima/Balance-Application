"""
Item class
Properties:
    name: string
    id: int
    price: float
Methods:
    set_name(name: string): None
    get_name(): string
    set_id(id: int): None
    get_id(): int
    set_price(price: float): None
    get_price(): float
"""
import json


class Item():
    def __init__(self, id, name, price=0):
        self.id = id
        self.name = name
        self.price = price

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price

    def item_to_json(self):
        item_json = {
            "name": self.get_name(),
            "price": self.get_price()
        }
        return item_json

    def json_to_item(json_string):
        return json.loads(json_string)
