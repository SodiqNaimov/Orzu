import sqlite3


from bot.utils.config import *
from telebot.storage import StateMemoryStorage
from telebot.types import KeyboardButton, ReplyKeyboardMarkup,\
    ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup

from users.choices import UserType


# db = sqlite3.connect(DATABASE)
# c = db.cursor()
#
# c.execute("""CREATE TABLE savat (
#            user_id text,
#            product_name text,
#            language    text,
#            count      text,
#            price      text
#            )""")
# db.commit()
# db.close()
# db = sqlite3.connect(DATABASE)
# cursor = db.cursor()
# # connection = sqlite3.connect('counter_data.db')
# # cursor = connection.cursor()
#
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS sorov (
#         user_id char(25),
#         mahsulot_zakasi INTEGER PRIMARY KEY
#     )
# ''')



class MyStates(StatesGroup):
    start = State()
    lang = State()
    user_data = State()
    settings = State()
    social_media_st = State()
    update_language=State()
    header_menu = State()
    complaint = State()
    complaint_handle_st = State()
    complaint_vocie = State()
    catalog_st = State()
    product = State()
    sub_catalog =State()
    product_show = State()
    basket = State()
    in_sub_catalog = State()
    in_pod_sub_catalog =State()
    back_from_products  =State()
    baskets_menu = State()
    in_product = State()
    back_from_products_second = State()
    basket_second = State()
    order_menu = State()
    phone = State()
    final = State()
    admin = State()
    admin_send = State()
    text_admin = State()
    photo = State()
    video =State()
    admin_send_btn = State()
    admin_send_photo_btn = State()
    admin_ask_button_name = State()
    admin_send_video_btn = State()
class SQLite:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.commit = self.connection.commit()
    def close(self):
        self.connection.close()
    def insert_to_users(self, user_id, language):
        with self.connection:
            self.cursor.execute("INSERT INTO users_user (telegram_id, language,type,is_superuser) VALUES (?,?,?,?)",
                                [user_id,language,UserType.CUSTOMER,False])

    def is_registered(self, user_id):
        with self.connection:
            self.cursor.execute("""SELECT telegram_id FROM users_user WHERE telegram_id = ? """, [user_id])
            rows = self.cursor.fetchall()

            return rows


    def calaculate_sum_user(self):
        with self.connection:
            self.cursor.execute("""SELECT user_id FROM users""")
            rows = self.cursor.fetchall()

            return len(rows)

    def send_user_message(self):
        with self.connection:
            self.cursor.execute("""SELECT user_id FROM users""")
            rows = self.cursor.fetchall()

            return rows
    def basket_user(self,user_id):
        with self.connection:
            self.cursor.execute("""SELECT product_name,count,price,total_price FROM savat WHERE user_id = ? """, [user_id])
            rows = self.cursor.fetchall()

            return rows

    def counter_month(self):
        with self.connection:
            self.cursor.execute('SELECT mahsulot_zakasi FROM sorov')
            rows = self.cursor.fetchall()

            return rows
    def insert_month(self,user_id):
        with self.connection:
            self.cursor.execute('INSERT INTO sorov (user_id) VALUES (?)',[user_id])

    def get_data_lang(self, user_id):
        with self.connection:
            self.cursor.execute("""SELECT language FROM users WHERE user_id = ? """, [user_id])
            rows = self.cursor.fetchall()

            return rows

    def update_data_lang(self,lang, user_id):
        with self.connection:
            self.cursor.execute("""UPDATE users SET language =? WHERE user_id = ? """, (lang, user_id))
            rows = self.cursor.fetchall()

            return rows

    def update_counter(self,today):
        with self.connection:
            self.cursor.execute('UPDATE counter SET monthly_count=current_count, current_count=0, last_reset_date=?', (today,))
            rows = self.cursor.fetchall()

            return rows

    def insert_baskets(self, user_id, product_name, count,price,total_price):
        with self.connection:
            self.cursor.execute("INSERT INTO savat (user_id, product_name,count,price,total_price) VALUES (?,?,?,?, ?)",
                                [user_id, product_name,count,price,total_price])

    def select_catalog(self,lang):
        with self.connection:
            if lang =='uz':
                self.cursor.execute("""SELECT name_uz FROM products_category WHERE parent_id  IS NULL""")
            if lang == 'ru':
                self.cursor.execute("""SELECT name_ru FROM products_category WHERE parent_id  IS NULL """)
            rows = self.cursor.fetchall()

            return rows

    def select_all_category(self,lang):
        with self.connection:
            if lang =='uz':
                self.cursor.execute("""SELECT name_uz FROM products_category""")
            if lang == 'ru':
                self.cursor.execute("""SELECT name_ru FROM products_category""")
            rows = self.cursor.fetchall()

            return rows
    def select_parent_id(self,lang,category):
        with self.connection:
            if lang =='uz':
                self.cursor.execute("""SELECT id FROM products_category Where name_uz == ?""", [category])
            if lang == 'ru':
                self.cursor.execute("""SELECT id FROM products_category Where name_ru == ?""", [category])
            rows = self.cursor.fetchall()

            return rows
    def select_category_parent_id(self,lang,parent_id):
        with self.connection:
            if lang =='uz':
                self.cursor.execute("""SELECT name_uz FROM products_category Where parent_id == ?""", [parent_id])
            if lang == 'ru':
                self.cursor.execute("""SELECT name_ru FROM products_category Where parent_id == ?""", [parent_id])
            rows = self.cursor.fetchall()

            return rows

    def select_sub_catalog(self,lang,text):
        with self.connection:
            if lang == 'uz':
                self.cursor.execute("""SELECT name_uz FROM products_category WHERE parent_id = ? """, [text])
            if lang == 'ru':
                self.cursor.execute("""SELECT name_ru FROM products_category WHERE parent_id = ? """, [text])

            rows = self.cursor.fetchall()

            return rows

    def get_parent_id_from_database(self, lang, text):
        with self.connection:
            if lang == 'uz':
                self.cursor.execute("""SELECT parent_id FROM products_category WHERE name_uz = ? """, [text])
            if lang == 'ru':
                self.cursor.execute("""SELECT parent_id  FROM products_category WHERE name_ru = ? """, [text])

            rows = self.cursor.fetchall()

            return rows

    def select_product(self,lang,text):
        with self.connection:
            if lang == 'uz':
                self.cursor.execute("""SELECT name_uz FROM products_product WHERE category_id == ?""", [text])
            if lang =='ru':
                self.cursor.execute("""SELECT name_uz FROM products_product WHERE category_id == ?""", [text])

            rows = self.cursor.fetchall()

            return rows
    def select_product_id(self,lang,text):
        with self.connection:
            if lang == 'uz':
                self.cursor.execute("""SELECT category_id  FROM products_product WHERE name_uz == ?""", [text])
            if lang =='ru':
                self.cursor.execute("""SELECT category_id  FROM products_product WHERE name_ru == ?""", [text])

            rows = self.cursor.fetchall()

            return rows

    def select_product_show(self,lang,text):
        with self.connection:
            if lang == 'uz':
                self.cursor.execute("""SELECT name_uz,description_uz,regular_price,image FROM products_product WHERE name_uz == ?""", [text])
            if lang == 'ru':
                self.cursor.execute("""SELECT name_ru,description_uz,regular_price,image FROM products_product WHERE name_uz == ?""", [text])

            rows = self.cursor.fetchall()

            return rows

    def delete_baskets(self,user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM savat WHERE user_id = ?", (user_id,))



