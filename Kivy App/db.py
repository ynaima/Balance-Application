from datetime import datetime
import mysql.connector
import calendar

class Database():
    def __init__(self, user="root", database_name="balance_db"):
        self.db = mysql.connector.connect(
                host= "localhost",
                user= user,
                passwd= "password",
                database=database_name
            )
        self.cursor = self.db.cursor(buffered=True)

    """
    Method: initialize
    Desc: The initialize method initializes the mysql database so that the correct tables
          are within the device storage before any operations take place. This is separate from
          the __init__ function because it just establishes the connection to the database, the
          database will not need to be recreated on every instantiation of a database object.
    """
    def initialize(self):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS balance_db")
        self.cursor.execute("USE balance_db")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(200),
            Email VARCHAR(200),
            PhoneNumber CHAR(10),
            PasswordHash VARCHAR(200),
            Salt VARCHAR(200),
            UserType INT NOT NULL CHECK (UserType BETWEEN 0 AND 1)
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS receipts(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                UserID INT, FOREIGN KEY(UserID) REFERENCES users(ID) ON DELETE CASCADE,
                Vendor VARCHAR(100),
                DateOfPurchase DATE,
                Total FLOAT(7,2),
                Category VARCHAR(30)
            )""")
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS items(
                ID INT AUTO_INCREMENT PRIMARY KEY,
                ReceiptID INT, FOREIGN KEY(ReceiptID) REFERENCES receipts(ID) ON DELETE CASCADE,
                Name VARCHAR(100),
                Price FLOAT(7,2)
        )""")

        self.cursor.execute("""CREATE USER IF NOT EXISTS root@localhost IDENTIFIED BY 'password'""")
        self.cursor.execute("""GRANT ALL PRIVILEGES ON *.* to root@localhost WITH GRANT OPTION""")
        self.db.commit()

    """
    Method: create_user_record
    Desc: This method inserts a new user record into the user table in the database
    Parameters:
        user - a User object that contains all the non-sensitive information for the user
        password - the hashed password for the user
        salt - the salt used to encode the password so it can be later used for authentication
    Returns:
        new_id - the ID of the user just added to the table, returns -1 if it was unsuccessful
    """
    def create_user_record(self, user, password, salt):
        new_id = -1
        if not self.user_exists(user.email):
            q = "INSERT INTO users (Name, Email, PhoneNumber, PasswordHash, Salt, UserType) VALUES (%s, %s, %s, %s, %s, %s)"
            v = (user.get_name(), user.get_email(), user.get_phone(), password, salt, user.get_type())
            self.cursor.execute(q, v)
            self.db.commit()
            new_id = self.cursor.lastrowid if self.cursor.rowcount > 0 else -1
        return new_id

    
    def create_receipt_record(self, receipt_data, user):
        new_id = -1
        date = datetime.strptime(receipt_data["date"], "%m/%d/%Y")
        self.cursor.execute("""INSERT INTO receipts (UserID, Vendor, DateOfPurchase, Total, Category)
        VALUES (%s, %s, %s, %s, %s)
        """, (user, receipt_data["vendor"], date, receipt_data["cost"], receipt_data["category"]))
        self.db.commit()
        new_id = self.cursor.lastrowid
        return new_id

    def create_item_record(self, item, receipt):
        self.cursor.execute("""INSERT INTO items (ReceiptID, Name, Price)
        VALUES (%s, %s, %s)
        """, (receipt, item["name"], item["price"]))
        self.db.commit()

    """
    Method: user_exists
    Desc: determines if a user exists by checking if a user with the same email is already
          in the table
    Parameters: 
        email - the email to check for existence
    Returns: boolean indicating if a record exists with the inserted email
    """
    def user_exists(self, email):
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return self.cursor.rowcount > 0

    """
    Method: get_public_user_info
    Desc: retrieves all non-sensitive info for a certain user from the user table using the user's ID
          this includes name, email, and phone number
    """
    def get_public_user_info(self, email):
        self.cursor.execute("SELECT ID, Name, PhoneNumber FROM users WHERE Email=%s", (email,))
        result = self.cursor.fetchall()
        return None if len(result) == 0 else result[0]


    """
    Method: retrieve_pass_info
    Desc: retrieves the encoded password and salt from the user table for the specified user
          to be used in authentication
    Parameters
        user_id - the ID of the user for which the password is to be pulled
    """
    def retrieve_pass_info(self, user_id):
        self.cursor.execute("SELECT PasswordHash FROM users WHERE ID=%s", (user_id,))
        return self.cursor.fetchone()[0]


    """
    Method: update_user_record
    Desc: updates a single record in the users table with the provided data as long as
          a record with the provided ID exists
    Parameters:
        user_id - the ID of the user for which info is to be updated
        name - the new name for the user record
        email - the new email for the user record
        phone - the new phone for the user record
    """
    def update_user_record(self, user_id, name, email, phone):
        self.cursor.execute("""UPDATE users
        SET Name=%s, Email=%s, PhoneNumber=%s
        WHERE ID=%s""", (name, email, phone, user_id))
        self.db.commit()

    """
    Method: _translate_dates
    Desc: Private helper function for retrieve_receipt_months method to translate retrieved records
          from a list of tuples to formatted date strings
    Parameters:
        dates - the list of (month, year) tuples to be converted to strings
    Returns:
        datestrings - the list of formatted date strings
    """
    def _translate_dates(self, dates):
        datestrings = []
        for date in dates:
            month = calendar.month_name[date[0]]
            datestrings.append(month + " " + str(date[1]))
        return datestrings

    """
    Method: retrieve_receipt_months
    Desc: retrieves all unique receipt month and year combinations for a given user
    Parameters:
        user - The ID of the user for which months are to be pulled
    Returns:
        datestrings - The list of unique month/year values
    """
    def retrieve_receipt_months(self, user):
        self.cursor.execute("""SELECT MONTH(DateofPurchase) AS Expr1, YEAR(DateOfPurchase) AS Expr2
        FROM receipts
        WHERE UserID=%s
        GROUP BY MONTH(DateOfPurchase), YEAR(DateOfPurchase)""", (user,))
        results = self.cursor.fetchall()
        datestrings = self._translate_dates(results)
        return datestrings

    """
    Method: retrieve_receipts_by_month
    Desc: retrieves all receipt records for a particular user within a given month
    Parameters:
        user: the ID of the user for which receipts must be retrieved
        date: the month/year combo for which we are filtering receipts (formatted as mm YYYY)
    Returns:
        The set of records in the table matching the user ID and date criteria
    """
    def retrieve_receipts_by_month(self, user, date):
        month, year = date.split(" ")
        self.cursor.execute("""SELECT *
        FROM receipts
        WHERE MONTHNAME(DateOfPurchase)=%s AND YEAR(DateOfPurchase)=%s AND UserID=%s
        """, (month, year, user))
        return self.cursor.fetchall()

    """
    Method: retrieve_receipt_categories
    Desc: retrieves all unique receipt categories for a given user
    Parameters:
        user - The ID of the user for which categories are to be pulled
    Returns:
        categories - the list of unique categories
    """
    def retrieve_receipt_categories(self, user):
        self.cursor.execute("""SELECT DISTINCT Category
        FROM receipts
        WHERE UserID=%s
        """, (user,))
        results = self.cursor.fetchall()
        categories = [result[0] for result in results]
        return categories

    """
    Method: retrieve_receipts_by_category
    Desc: retrieves all receipt records for a particular user that are within a given category
    Parameters:
        user: the ID of the user for which receipts must be retrieved
        category: the category for which we are filtering receipts
    Returns:
        The set of records in the table matching the user ID and category criteria
    """
    def retrieve_receipts_by_category(self, user, category):
        self.cursor.execute("""SELECT *
        FROM receipts
        WHERE Category=%s AND UserID=%s
        """, (category, user))
        return self.cursor.fetchall()

    """
    Method: retrieve_receipt_items
    Desc: retrieves all item records for a given receipt
    Parameters:
        receipt: the ID of the receipt items must be pulled for
    Returns:
        The set of records in the items table matching the receipt ID criteria
    """
    def retrieve_receipt_items(self, receipt):
        self.cursor.execute("""SELECT *
        FROM items
        WHERE ReceiptID=%s
        """, (receipt,))
        return self.cursor.fetchall()

    """
    Method: update_receipt_category
    Desc: updates a particular receipt record's category field with a given
          category
    Parameters:
        category: the updated category name for the receipt record
        receipt_id: the ID of the receipt that will receive the updated category
    """
    def update_receipt_category(self, category, receipt_id):
        self.cursor.execute("""UPDATE receipts
        SET Category=%s
        WHERE ID=%s""", (category, receipt_id))
        self.db.commit()

    """
    Method: remove_receipt_record
    Desc: removes a record from the receipt table with the given ID. Because of the cascade
          rule set on the foreign key of the items table, this will also delete any items for
          that receipt from the items table at the same time
    Parameters:
        receipt_id: the ID of the receipt that is to be removed
    """
    def remove_receipt_record(self, receipt_id):
        self.cursor.execute("""DELETE FROM receipts
        WHERE ID=%s
        """, (receipt_id,))
        self.db.commit()

    """
    Method: close
    Desc: closes the database connection to avoid data corruption
    """
    def close(self):
        self.db.close()