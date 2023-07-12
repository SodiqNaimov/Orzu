from bot.keyboards.markup_texts import *
from bot.utils.config import DATABASE
from telebot.types import KeyboardButton, ReplyKeyboardMarkup,\
    ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.user_data import *

def get_lang():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*lang_msg)
    return markup

def get_header(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*header_message[lang])
    return markup

def get_order_btn(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*order_btn[lang])
    markup.add(*back_btn[lang])
    return markup


def get_sozlamalar(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(*sozlamalr_button[lang])

    return markup

def get_kontakt_location(lang):
    markup = ReplyKeyboardMarkup(True, True, row_width=1)
    markup.add(*sozlamalr_button[lang])

    return markup

def get_location(lang):
    markup = ReplyKeyboardMarkup(True, True)
    btn = KeyboardButton(location_btn[lang], request_location=True)
    markup.add(btn)
    markup.add(*back_btn[lang])

    return markup
def get_contact(lang):
    markup = ReplyKeyboardMarkup(True, True)
    btn = KeyboardButton(contact_btn[lang], request_contact=True)
    markup.add(btn)
    markup.add(*back_btn[lang])
    return markup
def get_social_media(lang):
    markup = ReplyKeyboardMarkup(True, True, row_width=2)
    markup.add(*social_media_markup[lang])

    return markup

def get_complaint(lang):
    markup = ReplyKeyboardMarkup(True, True, row_width=2)
    markup.add(*complaint_markup[lang])

    return markup

def get_handle_complaint(lang):
    markup = ReplyKeyboardMarkup(True, True, row_width=2)
    markup.add(*back_btn[lang])

    return markup
def get_catalog(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    db = SQLite(DATABASE)
    row = db.select_catalog(lang)
    buttons = [i[0] for i in row]
    row_width = 2
    markup.add(*back_btn[lang])
    for i in range(0, len(buttons), row_width):
        markup.row(*buttons[i:i + row_width])
    return markup

#
def get_sub_catalog(lang,sub_text):
    db = SQLite(DATABASE)
    row = db.select_all_category(lang)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*back_btn[lang])
    for i in row:
        if sub_text == i[0]:
            parent_id = db.select_parent_id(lang, sub_text)
            parent_id = parent_id[0][0]  # Assuming the result is a single value
    similar_category = db.select_category_parent_id(lang, parent_id)
    buttons = [j[0] for j in similar_category]
    row_width = 2

    for k in range(0, len(buttons), row_width):
        markup.row(*buttons[k:k + row_width])

    return markup,buttons,parent_id
def get_second_sub_catalog(lang, sub_text):
    db = SQLite(DATABASE)
    row = db.select_all_category(lang)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*back_btn[lang])


    for i in row:
        if sub_text == i[0]:
            parent_id = db.select_parent_id(lang, sub_text)
            parent_id = parent_id[0][0]  # Assuming the result is a single value

    similar_category = db.select_category_parent_id(lang, parent_id)
    buttons = [j[0] for j in similar_category]
    row_width = 2

    # Check if the number of buttons is odd
    if len(buttons) % row_width != 0:
        # Move the last row to a new row at the beginning
        last_row_start_index = -(len(buttons) % row_width)
        last_row = buttons[last_row_start_index:]
        buttons = buttons[:last_row_start_index]
        markup.row(*last_row)

        # Add the last row as a new row at the beginning


    for k in range(0, len(buttons), row_width):
        markup.row(*buttons[k:k + row_width])

    return markup, buttons, parent_id




def get_back_catalog(lang,sub_text):
    db = SQLite(DATABASE)
    row = db.select_sub_catalog(lang,sub_text)
    buttons = [i[0] for i in row]
    row_width = 2
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*back_btn[lang])
    for i in range(0, len(buttons), row_width):
        markup.row(*buttons[i:i + row_width])
    return markup

def get_sec_back_catalog(lang,sub_text):
    db = SQLite(DATABASE)
    row = db.select_sub_catalog(lang, sub_text)
    buttons = [i[0] for i in row]
    row_width = 2
    markup = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    markup.add(*back_btn[lang])

    # Check if the number of buttons is odd
    if len(buttons) % row_width != 0:
        # Move the last row to a new row at the beginning
        last_row_start_index = -(len(buttons) % row_width)
        last_row = buttons[last_row_start_index:]
        buttons = buttons[:last_row_start_index]

        # Add the last row as a new row at the beginning
        markup.row(*last_row)

    for i in range(0, len(buttons), row_width):
        markup.row(*buttons[i:i + row_width])

    return markup

def get_products(lang, products):
    db = SQLite(DATABASE)
    row = db.select_all_category(lang)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*back_btn[lang])
    for i in row:
        if products == i[0]:
            parent_id = db.select_parent_id(lang, products)
            parent_id = parent_id[0][0]  # Assuming the result is a single value

    similar_product = db.select_product(lang, parent_id)
    buttons = [j[0] for j in similar_product]
    row_width = 2
    for k in range(0, len(buttons), row_width):
        markup.row(*buttons[k:k + row_width])
    return markup,parent_id

def get_last_products(lang, products):

    db =SQLite(DATABASE)
    row = db.select_product(lang,products)
    buttons = [i[0] for i in row]
    row_width = 2
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*back_btn[lang])
    for i in range(0, len(buttons), row_width):
        markup.row(*buttons[i:i + row_width])

    return markup



def get_number(lang):
    markup = ReplyKeyboardMarkup(True, True, row_width=3)
    markup.add(*back_btn[lang])
    markup.add('1', '2', '3', '4','5')
    # markup.add('5')


    return markup


def get_baskets(lang):
    markup = ReplyKeyboardMarkup(True, True, row_width=2)
    markup.add(*baskets_btn[lang])
    return markup

def get_admin_btn():
    markup = ReplyKeyboardMarkup(True,row_width=2)
    markup.add(*admin_btn)
    return markup
def get_admin_send():
    markup = ReplyKeyboardMarkup(True,row_width=2)
    markup.add(*admin_back_btn)
    markup.add(*admin_send_btn)
    return markup

def back():
    markup = ReplyKeyboardMarkup(True,row_width=2)
    markup.add(*admin_back_btn)
    return markup

def get_admin_btn_inline():
    markup = ReplyKeyboardMarkup(True,row_width=2)
    markup.add(*admin_back_btn)
    markup.add(*admin_send_btn_inline)
    return markup