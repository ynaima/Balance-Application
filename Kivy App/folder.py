from copy import deepcopy
from receipt import Receipt

"""
Folder class
Properties:
    name: string
    id: int
    contents: Array<Receipt>
Methods:
    set_name(name: string): None
    get_name(): string
    set_id(id: int): None
    get_id(): int
    get_contents(): Array<Receipt>
    add_receipt(receipt: Receipt): None
    remove_receipt(receipt_id: int): boolean
"""
class Folder():
    def __init__(self, id, name):
        self.name = name
        self.id = id
        self.contents = []
    
    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def get_contents(self):
        #Uses deepcopy to prevent unwanted alteration of contents
        return deepcopy(self.contents)
    
    """
    Method: add_receipt
    Desc: adds a receipt to the folder objects contents
    Parameters:
        receipt: the Receipt object to be added to the folder contents
    """
    def add_receipt(self, receipt):
        self.contents.append(receipt)
    
    """
    Method: remove_receipt
    Desc: removes a receipt with the provided id from the folder if it exists
    Parameters:
        receipt_id - the id of the Receipt object that is to be removed from the folder
    Returns:
        removed - a boolean indicating whether or not the removal was successful
    """
    def remove_receipt(self, receipt_id):
        removed = False
        i = 0
        while not removed and i < len(self.contents):
            if self.contents[i].id == receipt_id:
                self.contents.pop(i)
                removed = True
            i += 1
        return removed