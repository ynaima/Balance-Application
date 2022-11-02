import json
from item import Item
from copy import deepcopy

"""
Receipt class
Properties:
    id: int
    vendor: string
    date: string
    cost: float
    category: string
Methods:
    set_id(id: int): None
    get_id(): int
    set_vendor(vendor: string): None
    get_vendor(): string
    set_date(date: string): None
    get_date(): string
    set_cost(price: float): None
    get_cost(): float
    get_items(): Array<Item>
    add_item(item: Item): None
"""
class Receipt():
    def __init__(self, id, vendor, date, cost, category = None):
        self.id = id
        self.vendor = vendor
        self.category = category
        self.date = date
        self.cost = cost
        self.items = []

    def get_id(self):
        return self.id
    
    def get_vendor(self):
        return self.vendor
    
    def set_vendor(self, vendor_name):
        self.vendor = vendor_name
    
    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date

    def get_cost(self):
        return self.cost
    
    def set_cost(self, cost):
        self.cost = cost

    def get_category(self):
        return self.category

    def set_category(self, category):
        self.category = category
    
    def get_items(self):
        #Uses deepcopy to prevent unwanted alteration of items
        return deepcopy(self.items)

    def format_date(self):
        return self.date.strftime("%m/%d/%Y")

    def receipt_to_json(self):
        receipt_json = {
            "vendor": self.get_vendor(),
            "category": self.get_category(),
            "date": self.format_date(),
            "cost": self.get_cost(),
            "items": [item.item_to_json() for item in self.get_items()]
        }
        return receipt_json

    def json_to_receipt(json_string):
        return json.loads(json_string)
    
    """
    Method: add_item
    Desc: adds a provided item to the receipts item list
    Parameters:
        item - the Item object to be added to the receipt
    """
    def add_item(self, item):
        self.items.append(item)