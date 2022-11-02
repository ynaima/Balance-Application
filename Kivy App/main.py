import json
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

import bcrypt
import os
from functools import partial

from db import Database
from copy import deepcopy
from receipt import Receipt
from item import Item
from user import User

WIDTH = 300
HEIGHT = 666
Window.clearcolor = (0.4, 0.31, 0.65, 1) #bg color
Window.size = (WIDTH, HEIGHT) #sets size to 20:9 display

class WelcomeScreen(Screen):
    pass

class WelcomeLayout(Widget):
    pass

class LoginLayout(Widget):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    authorized = ObjectProperty(False)

    def show_popup(self):
        show = LoginPopUp()
        window = Popup(title="Invalid Entry", content=show)
        window.open()

    def valid_form(self):
        valid = True
        if self.email.text is None or not User.valid_email(self.email.text):
            valid = False
        elif self.password.text is None or not User.valid_password(self.password.text):
            valid = False
        return valid

    def validate_password(self, password, check_pass):
        return bcrypt.checkpw(password.encode('utf-8'), check_pass.encode('utf-8'))

    def login(self):
        if self.valid_form():
            db = Database("root", "balance_db")
            if db.user_exists(self.email.text):
                user_id, name, phoneNum = db.get_public_user_info(self.email.text)
                check_pass = db.retrieve_pass_info(user_id)
                if self.validate_password(self.password.text, check_pass):
                    sm.current = "home"
                    sm.authorized_user = User(email=self.email.text, name=name, id=user_id, phone=phoneNum)
                else:
                    self.show_popup()
            else:
                self.show_popup()
            db.close()
        else:
            self.show_popup()


class SignUpLayout(Widget):
    email = ObjectProperty(None)
    phone = ObjectProperty(None)
    password = ObjectProperty(None)
    password_confirm = ObjectProperty(None)

    def validForm(self):
        valid = True
        if self.email.text is None or not User.valid_email(self.email.text):
            valid = False
        elif self.phone.text is None or not User.valid_phone(self.phone.text):
            valid = False
        elif self.password.text is None or not User.valid_password(self.password.text):
            valid = False
        elif self.password.text != self.password_confirm.text:
            valid = False
        return valid

    def signup(self):
        db = Database("root", "balance_db")
        if self.validForm():
            print("HERE")
            if not db.user_exists(self.email.text):
                user = User("", self.email.text, self.phone.text)
                new_id = db.create_user_record(user, *User.hash_password(self.password.text))
                user.set_id(new_id)
                sm.authorized_user = user
                sm.current = "home"
        db.close()

class LoginScreen(Screen):
    pass
    
class SignUpScreen(Screen):
    pass


class LoadDialog(GridLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class HomeScreen(Screen):

    def dismiss_popup(self):
        self._popup.dismiss()
    
    def receive_receipt(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Find Receipt", content=content)
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            receipt_text = stream.read()
            receipt_dict = Receipt.json_to_receipt(receipt_text)
            db = Database()
            receipt_id = db.create_receipt_record(receipt_dict, sm.authorized_user.get_id())
            for item in receipt_dict["items"]:
                db.create_item_record(item, receipt_id)
            db.close()

        self.dismiss_popup()


class AddReceiptScreen(Screen):
    pass


class ViewCategoriesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        self.ids.category_list.data = [{'text': category, 'on_release': partial(self.get_receipts_by_category, category)} for category in self.get_category_list()]
        self.ids.category_list.refresh_from_data()
    
    def get_category_list(self):
        db = Database()
        categories = db.retrieve_receipt_categories(sm.authorized_user.get_id())
        db.close()
        return categories

    def get_receipts_by_category(self, category):
        db = Database()
        receipt_tuples = db.retrieve_receipts_by_category(sm.authorized_user.get_id(), category)
        sm.receipt_list = [Receipt(receipt[0], receipt[2], receipt[3], receipt[4], receipt[5]) for receipt in receipt_tuples]
        db.close()
        sm.current = "receipts"

class ViewMonthsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        self.ids.month_list.data = [{'text': month, 'on_release': partial(self.get_receipts_by_month, month)} for month in self.get_month_list()]
        self.ids.month_list.refresh_from_data()

    def get_month_list(self):
        db = Database()
        months = db.retrieve_receipt_months(sm.authorized_user.get_id())
        db.close()
        return months

    def get_receipts_by_month(self, month):
        db = Database()
        receipt_tuples = db.retrieve_receipts_by_month(sm.authorized_user.get_id(), month)
        sm.receipt_list = [Receipt(receipt[0], receipt[2], receipt[3], receipt[4], receipt[5]) for receipt in receipt_tuples]
        db.close()
        sm.current = "receipts"

class ViewReceiptsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_pre_enter(self):
        self.ids.receipt_list.data = [{
            'text': receipt.vendor + "\n" + str(receipt.cost), 
            'on_release': partial(self.get_receipt_items, receipt.get_id())} 
            for receipt in self.get_receipt_list()]
        self.ids.receipt_list.refresh_from_data()

    def get_receipt_list(self):
        return deepcopy(sm.receipt_list)

    def get_receipt_items(self, receipt_id):
        db = Database()
        for receipt in sm.receipt_list:
            if receipt.id == receipt_id:
                sm.selected_receipt = deepcopy(receipt)
                break
        
        items = db.retrieve_receipt_items(receipt_id)
        for item in items:
            sm.selected_receipt.add_item(Item(item[0], item[2], item[3]))
        db.close()
        sm.current = "receipt"


class SaveDialog(GridLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)

class DeleteDialog(GridLayout):
    delete = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ViewReceiptScreen(Screen):
    def on_pre_enter(self):
        self.ids.receipt_vendor.text = sm.selected_receipt.vendor
        self.ids.receipt_date.text = sm.selected_receipt.format_date()
        self.ids.item_list.data = [{'text': item.name + " "*10 + str(item.price)} for item in sm.selected_receipt.get_items()]
        self.ids.item_list.refresh_from_data()

    def dismiss_popup(self):
        self._popup.dismiss()

    def share_receipt(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save Receipt", content=content)
        self._popup.open()

    def show_delete_popup(self):
        content = DeleteDialog(delete=self.delete_receipt, cancel=self.dismiss_popup)
        self._popup = Popup(title="Confirm Delete", content=content)
        self._popup.open()
    
    def save(self, path, filename):
        receipt_json = sm.selected_receipt.receipt_to_json()
        with open(os.path.join(path, filename), 'w') as stream:
            print(receipt_json)
            stream.write(json.dumps(receipt_json))

        self.dismiss_popup()

    def delete_receipt(self):
        db = Database()
        db.remove_receipt_record(sm.selected_receipt.get_id())
        db.close()
        sm.current = "home"
        sm.selected_receipt = None
        self.dismiss_popup()


class CategorizeReceiptScreen(Screen):
    new_category_input = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_pre_enter(self):
        self.ids.receipt_category.text = sm.selected_receipt.category if sm.selected_receipt.category is not None else ""
        self.ids.categorize_list.data = [{'text': category, 'on_release': partial(self.update_selected_category, category)} for category in self.get_category_list()]
        self.ids.categorize_list.refresh_from_data()

    def get_category_list(self):
        db = Database()
        categories = db.retrieve_receipt_categories(sm.authorized_user.get_id())
        db.close()
        return categories
    
    def update_selected_category(self, category):
        self.ids.receipt_category.text = category

    def add_new_category(self):
        categories = self.get_category_list()
        if self.new_category_input.text not in categories and self.new_category_input.text != "":
            self.ids.categorize_list.data.append({'text': self.new_category_input.text, 'on_release': partial(self.update_selected_category, self.new_category_input.text)})
            self.ids.categorize_list.refresh_from_data()
            self.ids.receipt_category.text = self.new_category_input.text
            self.ids.new_category_input.text = ""

    def update_category_record(self):
        if self.ids.receipt_category.text != sm.selected_receipt.category:
            db = Database()
            sm.selected_receipt.set_category(self.ids.receipt_category.text)
            db.update_receipt_category(self.ids.receipt_category.text, sm.selected_receipt.id)
            db.close()

class ViewSettingsScreen(Screen):
    username = StringProperty("")
    email = StringProperty("")
    phone = StringProperty("")

    def on_pre_enter(self):
        self.load_label_values()

    def load_label_values(self):
        self.username = self.parent.authorized_user.get_name()
        self.email = self.parent.authorized_user.get_email()
        self.phone = self.parent.authorized_user.get_phone()


class EditSettingsScreen(Screen):
    username = StringProperty("")
    email = StringProperty("")
    phone = StringProperty("") 
    
    _username = ObjectProperty()
    _email = ObjectProperty()
    _phone = ObjectProperty()

    def on_pre_enter(self):
        self.load_input_values()
    
    def load_input_values(self):
        self.username = self.parent.authorized_user.get_name()
        self.email = self.parent.authorized_user.get_email()
        self.phone = self.parent.authorized_user.get_phone()

    def update_user_info(self):
        self.parent.authorized_user.set_name(self._username.text)
        self.parent.authorized_user.set_email(self._email.text)
        self.parent.authorized_user.set_phone(self._phone.text)

        db = Database()
        db.update_user_record(self.parent.authorized_user.get_id(), self._username.text, self._email.text, self._phone.text)
        db.close()


class AppBar(Widget):
    pass

class LoginPopUp(GridLayout):
    pass

class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.authorized_user = User()
        self.receipt_list = []
        self.selected_receipt = None



kv = Builder.load_file("balance.kv")
sm = WindowManager()
sm.add_widget(WelcomeScreen(name="welcome"))
sm.add_widget(SignUpScreen(name="signup"))
sm.add_widget(LoginScreen(name="login"))
sm.add_widget(HomeScreen(name="home"))
sm.add_widget(ViewSettingsScreen(name="settings"))
sm.add_widget(EditSettingsScreen(name="profile"))
sm.add_widget(ViewMonthsScreen(name="months"))
sm.add_widget(ViewCategoriesScreen(name="categories"))
sm.add_widget(ViewReceiptsScreen(name="receipts"))
sm.add_widget(ViewReceiptScreen(name="receipt"))
sm.add_widget(CategorizeReceiptScreen(name="categorize"))

class BalanceApp(App):
    def build(self):
        self.icon = 'BalanceIcon.png'
        mydb = Database("root", "balance_db")
        mydb.initialize()
        mydb.close()
        return sm

if __name__ == "__main__":
    BalanceApp().run()