from db import Database
import bcrypt
import re

"""
User class
Properties:
    name: string
    email: string
    phone: string
    type: int
    id: int
Methods:
    set_name(name: string): None
    get_name(): string
    set_email(email: string): None
    get_email(): string
    set_phone(phone: string): None
    get_phone(): String
    set_type(type: int): None
    get_type(): int
    set_id(id: int): None
    get_id(): int
    vald_phone(phone: string): boolean
    valid_email(email: string): boolean
    valid_password(password: string): boolean
    hash_password(password: string): string
    authenticate(password: string): boolean
"""
class User():
    def __init__(self, name="", email="", phone="", type=0, id=0):
        self.name = name
        self.email = email
        self.phone = phone
        self.type = type
        self.id = id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_email(self, email):
        if User.valid_email(email):
            self.email = email
    
    def get_email(self):
        return self.email

    def set_phone(self, number):
        if User.valid_phone(number):
            self.phone = number

    def set_type(self, type):
        #Valid types are only 0 for buyer and 1 for seller
        if type == 0 or type == 1:
            self.type = type

    def get_type(self):
        return self.type

    def get_phone(self):
        return self.phone

    def set_id(self, id):
        self.id = id
    
    def get_id(self):
        return self.id

    """
    Method: valid_phone
    Desc: determines if a provided phone number is valid. A phone number is said to be valid
          if it contains 10 digits and could be converted to a numeric form
    Parameters:
        number - the phone number to be checked for validity
    Returns:
        boolean representing the validity of the provided number
    """
    def valid_phone(number):
        return len(number) == 10 and number.isnumeric()

    """
    Method: valid_email
    Desc: determines if a provided phone number is valid. An email is said to be valid if it matches the
          regex string which cuts out special characters, requires the @ symbol and the .
    Parameters:
        email - the email to be checked for validity
    Returns:
        boolean representing the validity of the provided email
    """
    def valid_email(email):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        return re.fullmatch(regex, email)

    """
    Method: valid_password
    Desc: determines if a provided password is valid. The only requirement for valid password is having a
          length of 8 characters or more
    Parameters:
        password - the password to be checked for validity
    Returns:
        boolean representing the validity of the provided password
    """
    def valid_password(password):
        return len(password) > 7

    """
    Method: hash_password
    Desc: encrypts a given password using bcrypt hashing and salting to protect
          against malicious actors
    Parameters:
        password - the password to be encrypted
    Returns:
        salt - the salt used to encrypt the password
        encode_pass - the encrypted password string
    """
    def hash_password(password):
        salt = bcrypt.gensalt()
        encode_pass = bcrypt.hashpw(password.encode('utf-8'), salt)
        return (encode_pass, salt)

    """
    Method: authenticate
    Desc: determines if the user object can be authenticated provided a certain password
    Parameters:
        password - the password to use to attempt authentication of the user object
    Returns:
        result - a boolean indicating whether or not authentication was successful
    """
    def authenticate(self, password):
        result = False
        if self.valid_email(self.email) and self.valid_password(password):
            db = Database("root", "balance_db") #Open database instance
            password_info = db.retrieve_pass_info(self.get_id())
            if bcrypt.hashpw(password, password_info[1]) == password_info[0]: #Check that hashed passwords match
                result = True
            db.close()
        return result

        
