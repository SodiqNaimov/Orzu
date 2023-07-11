import telebot
from geopy.geocoders import Nominatim,Photon
from bot.utils.config import BOT,DATABASE
from bot.texts.messages import *
from bot.utils.user_data import *
from bot.keyboards.reply_markup import *
from telebot import custom_filters
bot = telebot.TeleBot(BOT,num_threads=2,parse_mode="HTML")
basket_to_user = {}
lang = {}
data = {}
btn_back = {}
select_user = {}
type_deliver = {}
user_dict = {}

class ConversationState:
    def __init__(self):
        self.photo_id = None
        self.caption = None
        self.buttons = []
        self.video_id = None
state = ConversationState()

@bot.message_handler(commands=['start'])
def start(message):
    global lang
    basket_to_user[message.chat.id] = []
    # Получаем текущую дату
    # today = datetime.date.today().strftime('%Y-%m-%d')
    # db = SQLite(DATABASE)
    # last_reset_date = db.counter()
    #
    # # Если текущая дата больше даты последнего сброса, выполняем сброс счетчика
    # if today > last_reset_date:
    #     db.update_counter(today)
    db = SQLite(DATABASE)
    is_register = db.is_registered(message.chat.id)
    if len(is_register) == 0:
        msg = bot.send_message(message.chat.id, start_msg, reply_markup=get_lang())
        bot.set_state(message.from_user.id, MyStates.lang, message.chat.id)

    else:
        rows = db.get_data_lang(message.chat.id)
        lang[message.chat.id] =rows[0][0]
        header(message)
    # bot.send_message(message.chat.id, start_msg)

@bot.message_handler(state=MyStates.lang)
def get_language(message):

    global lang
    global user_data
    if message.text in lang_msg:
        if message.text == lang_msg[1]:
            lang[message.chat.id] = 'ru'
            db = SQLite(DATABASE)
            db.insert_to_users(message.chat.id, "ru")
            bot.set_state(message.from_user.id, MyStates.user_data, message.chat.id)

        if message.text == lang_msg[0]:
            lang[message.chat.id] = 'uz'
            db = SQLite(DATABASE)
            db.insert_to_users(message.chat.id, "uz")

            bot.set_state(message.from_user.id, MyStates.user_data, message.chat.id)
    header(message)

@bot.message_handler(state=MyStates.user_data)
def header(message):
    global lang
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],reply_markup=get_header(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.header_menu, message.chat.id)

@bot.message_handler(state=MyStates.header_menu,text=["🛒 Savat", "🛒 Корзина"])
def basket(message):
    db = SQLite(DATABASE)
    rows = db.basket_user(message.chat.id)
    if len(rows) == 0:
        bot.send_message(message.chat.id, basket_message[lang[message.chat.id]])
        header(message)
    else:
        text = ''
        num = 1
        for i in rows:
            name = i[0]
            count = i[1]
            price = i[2]
            all_cost = int(price) * int(i[1])
            number = price
            formatted_number = "{:,.0f}".format(number).replace(",", " ")
            number1 = all_cost
            formatted_number1 = "{:,.0f}".format(number1).replace(",", " ")
            text += str(num) + ') ' + "<b>" + name + "</b>" +'\n' + count + ' x ' + "<b>" +formatted_number +"</b>" +"<b>" +" so'm" + "</b>"+ ' = ' + str(
                "<b>" + formatted_number1 + "</b>") +"<b>" +" so'm" + "</b>"+ '\n\n'
            num += 1
        overall_cost = []

        for j in rows:
            overall_cost.append(int(j[3]))
        number2 = sum(overall_cost)
        formatted_number2 = "{:,.0f}".format(number2).replace(",", " ")
        bot.send_message(message.chat.id, basket_count_message[lang[message.chat.id]].format(text,formatted_number2),reply_markup=get_baskets(lang[message.chat.id]))
        bot.send_message(message.chat.id, baskets_info[lang[message.chat.id]])
        bot.set_state(message.from_user.id, MyStates.baskets_menu, message.chat.id)
@bot.message_handler(state=MyStates.baskets_menu,text = ["📤 Buyurtmani yakunlash","📤 Оформить заказ"])
def order(message):
    bot.send_message(message.chat.id, order_message[lang[message.chat.id]],reply_markup=get_order_btn(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.order_menu, message.chat.id)
    type_deliver[message.chat.id] = []

@bot.message_handler(state=MyStates.order_menu,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from(message):
    basket(message)

@bot.message_handler(state=MyStates.order_menu)
def delivery(message):
    type_deliver[message.chat.id] = message.text
    bot.send_message(message.chat.id, deleivery_message[lang[message.chat.id]],reply_markup=get_location(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.phone, message.chat.id)
    user_dict[message.chat.id] = {'Latitude':'','Longitude':'','location':'','phone_number':''}
@bot.message_handler(state=MyStates.phone,text = ["⬅️ Ortga","⬅️ Назад"])
def back_delivery(message):
    order(message)


@bot.message_handler(state=MyStates.phone,content_types=['location'])
def send_phone_number(message):
    print(type_deliver[message.chat.id])
    geolocatr = Photon(user_agent='geoapiExercises')
    Latitude = message.location.latitude
    Longitude = message.location.longitude
    location = geolocatr.reverse(str(Latitude) + "," + str(Longitude))



    user_dict[message.chat.id]['location'] = location
    user_dict[message.chat.id]['Longitude'] = Longitude
    user_dict[message.chat.id]['Latitude'] = Latitude
    bot.send_message(message.chat.id,phone_message[lang[message.chat.id]],reply_markup=get_contact(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.final, message.chat.id)

@bot.message_handler(state=MyStates.final)
def final_second(message):
    user_dict[message.chat.id]['phone_number'] = message.text
    adrdress_phone = "📍Адрес: " + str(user_dict[message.chat.id]['location']) + '\n' + '📱 Номер телефона: ' + str(user_dict[message.chat.id]['phone_number'])
    bot.send_location(-963466862, user_dict[message.chat.id]['Latitude'],  user_dict[message.chat.id]['Longitude'])
    db = SQLite(DATABASE)
    rows = db.basket_user(message.chat.id)
    db.insert_month(message.chat.id)
    text = ''
    num = 1
    for i in rows:
        name = i[0]
        count = i[1]
        price = i[2]
        all_cost = int(price) * int(i[1])


        number = price
        formatted_number = "{:,.0f}".format(number).replace(",", " ")

        number1 = all_cost
        formatted_number1 = "{:,.0f}".format(number1).replace(",", " ")
        text += str(
            num) + ') ' + "<b>" + name + "</b>" + '\n' + count + ' x ' + "<b>" + formatted_number+ "</b>" + "<b>" + " so'm" + "</b>" + ' = ' + str(
            "<b>" +formatted_number1 + "</b>") + "<b>" + " so'm" + "</b>" + '\n\n'
        num += 1
    text_2 = ''
    num = 1
    for i in rows:
        name = i[0]
        count = i[1]
        price = i[2]
        all_cost = int(price) * int(i[1])


        number = price
        formatted_number = "{:,.0f}".format(number).replace(",", " ")

        number1 = all_cost
        formatted_number1 = "{:,.0f}".format(number1).replace(",", " ")
        text_2 += str(
            num) + ') ' + "*" + name + "*" + '\n' + count + ' x ' + "*" + formatted_number + "*" + "*" + " so'm" + "*" + ' = ' + str(
            "*" + formatted_number1 + "*") + "*" + " so'm" + "*" + '\n\n'
        num += 1
    overall_cost = []
    for j in rows:
        overall_cost.append(int(j[3]))

    number2 = sum(overall_cost)
    formatted_number2 = "{:,.0f}".format(number2).replace(",", " ")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    silka = message.from_user.username
    db = SQLite(DATABASE)
    raqamcha =  db.counter_month()
    for i in raqamcha:
        order_number = i[0]

    if message.from_user.username == None:
        bot.send_message(-963466862,
                         f"*Yangi buyurtma!\n\n🧾* *Buyurtma raqami:* *#000{str(order_number)}* *\n\n{text_2}* *Jami:* *{str(formatted_number2)} so'm* \n\n{str(adrdress_phone)} \n👤 *Telegram account*: {mention} \n📲 Buyurtma berish turi: *{type_deliver[message.chat.id]}*",
                         parse_mode="Markdown")

    else:
        # bot.send_message(-963466862,
        #                  f"*Yangi buyurtma!\n\n🧾* *Buyurtma raqami:* *#000{str(order_number)}* *\n\n{text}* *Jami:* *{str(d3)} so'm* \n\n{str(adrdress_phone)} \n👤 *Telegram account*: {mention} \n📲 Buyurtma berish turi: *{type_deliver[message.chat.id]}*",
        #                  parse_mode="Markdown")
        bot.send_message(-963466862,
                         "<b>Yangi buyurtma! \n\n🧾 Buyurtma raqami: </b>" + '<b>' + '#000' + str(order_number) + '</b>' + '\n\n' + text + " <b>Jami</b>: " + "<b>" + str(formatted_number2) + "</b>" + "<b> so'm</b> " + "\n\n" + adrdress_phone + "\n👤 <b>Telegram account: @</b>" + silka + "<b>\n📲 Buyurtma berish turi: </b>" + "<b>" + type_deliver[message.chat.id] + "</b>",
                         parse_mode="HTML")
    bot.send_message(message.chat.id, final_message[lang[message.chat.id]].format(text,formatted_number2))
    db = SQLite(DATABASE)
    db.delete_baskets(message.chat.id)
    type_deliver[message.chat.id] = []
    user_dict[message.chat.id] = []
    header(message)










@bot.message_handler(state=MyStates.final,content_types=['contact'])
def final(message):
    user_dict[message.chat.id]['phone_number'] = message.contact.phone_number
    adrdress_phone = "📍Адрес: " + str(user_dict[message.chat.id]['location']) + '\n' + '📱 Номер телефона: ' + str(user_dict[message.chat.id]['phone_number'])
    bot.send_location(-963466862, user_dict[message.chat.id]['Latitude'],  user_dict[message.chat.id]['Longitude'])
    db = SQLite(DATABASE)
    rows = db.basket_user(message.chat.id)
    db.insert_month(message.chat.id)

    text = ''
    num = 1
    for i in rows:
        name = i[0]
        count = i[1]
        price = i[2]
        all_cost = int(price) * int(i[1])

        number = price
        formatted_number = "{:,.0f}".format(number).replace(",", " ")

        number1 = all_cost
        formatted_number1 = "{:,.0f}".format(number1).replace(",", " ")

        text += str(
            num) + ') ' + "<b>" + name + "</b>" + '\n' + count + ' x ' + "<b>" + formatted_number + "</b>" + "<b>" + " so'm" + "</b>" + ' = ' + str(
            "<b>" + formatted_number1 + "</b>") + "<b>" + " so'm" + "</b>" + '\n\n'
        num += 1
    text_2 = ''
    num = 1
    for i in rows:
        name = i[0]
        count = i[1]
        price = i[2]
        all_cost = int(price) * int(i[1])

        number = price
        formatted_number = "{:,.0f}".format(number).replace(",", " ")

        number1 = all_cost
        formatted_number1 = "{:,.0f}".format(number1).replace(",", " ")

        text_2 += str(
            num) + ') ' + "*" + name + "*" + '\n' + count + ' x ' + "*" + formatted_number + "*" + "*" + " so'm" + "*" + ' = ' + str(
            "*" + formatted_number1 + "*") + "*" + " so'm" + "*" + '\n\n'
        num += 1
    overall_cost = []
    for j in rows:
        overall_cost.append(int(j[3]))


    number2 = sum(overall_cost)
    d3 = "{:,.0f}".format(number2).replace(",", " ")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    silka = message.from_user.username
    db = SQLite(DATABASE)
    raqamcha = db.counter_month()
    for i in raqamcha:
        order_number = i[0]

    if message.from_user.username == None:
        bot.send_message(-963466862,
                         f"*Yangi buyurtma!\n\n🧾* *Buyurtma raqami:* *#000{str(order_number)}* *\n\n{text_2}* *Jami:* *{str(d3)} so'm* \n\n{str(adrdress_phone)} \n👤 *Telegram account*: {mention} \n📲 Buyurtma berish turi: *{type_deliver[message.chat.id]}*",
                         parse_mode="Markdown")

    else:
        # bot.send_message(-963466862,
        #                  f"*Yangi buyurtma!\n\n🧾* *Buyurtma raqami:* *#000{str(order_number)}* *\n\n{text}* *Jami:* *{str(d3)} so'm* \n\n{str(adrdress_phone)} \n👤 *Telegram account*: {mention} \n📲 Buyurtma berish turi: *{type_deliver[message.chat.id]}*",
        #                  parse_mode="Markdown")
        bot.send_message(-963466862,
                         "<b>Yangi buyurtma! \n\n🧾 Buyurtma raqami: </b>" + '<b>' + '#000' + str(order_number) + '</b>' + '\n\n' + text + " <b>Jami</b>: " + "<b>" + str(d3) + "</b>" + "<b> so'm</b> " + "\n\n" + adrdress_phone + "\n👤 <b>Telegram account: @</b>" + silka + "<b>\n📲 Buyurtma berish turi: </b>" + "<b>" + type_deliver[message.chat.id] + "</b>",
                         parse_mode="HTML")
    bot.send_message(message.chat.id, final_message[lang[message.chat.id]].format(text,d3))
    db = SQLite(DATABASE)
    db.delete_baskets(message.chat.id)
    type_deliver[message.chat.id] = []
    user_dict[message.chat.id] = []
    header(message)







@bot.message_handler(state=MyStates.final,text = ["⬅️ Ortga","⬅️ Назад"])
def back_send_phone_number(message):
    delivery(message)




@bot.message_handler(state=MyStates.baskets_menu,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_basket(message):
    header(message)

@bot.message_handler(state=MyStates.baskets_menu,text = ["♻️ Очистить Корзину","♻️ Savatni tozalash"])
def delete_from_user(message):
    db = SQLite(DATABASE)
    db.delete_baskets(message.chat.id)
    bot.send_message(message.chat.id, baskets_info_when_delete[lang[message.chat.id]])
    header(message)

############################################################Cataolog
@bot.message_handler(state=MyStates.header_menu,text=["📙 Katalog", "📙 Каталог"])
def catalog(message):
    btn_back[message.chat.id] = {'back_catalog':'','back_sub_catalog':'','back_in_sub_catalog_show':'','back_in_pod_sub_catalog_show':'','back_from_product':'','back_from_basket':'',
                                 'back_man_in_sub_catalog_show':''}

    bot.send_message(message.chat.id, catalog_message[lang[message.chat.id]],reply_markup=get_catalog(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.catalog_st, message.chat.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

@bot.message_handler(state=MyStates.catalog_st,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_catalog(message):
    header(message)
############################################################Cataolog






############################################################catalog_menu

@bot.message_handler(state=MyStates.catalog_st)
def catalog_menu(message):
    # print(btn_back[message.chat.id])
    print(message.message_id)
    print(message)
    # bot.edit_message_text
    btn_back[message.chat.id]['back_catalog'] = get_sub_catalog(lang[message.chat.id], message.text)[2]
    # bot.edit_message_text(text="1", chat_id=message.chat.id, message_id=message.message_id - 2)
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_sub_catalog(lang[message.chat.id],message.text)[0])
    bot.set_state(message.from_user.id, MyStates.sub_catalog, message.chat.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

@bot.message_handler(state=MyStates.sub_catalog,text = ["⬅️ Ortga","⬅️ Назад"])
def back_catalog_menu(message):
    catalog(message)
############################################################catalog_menu








############################################################sub_catalog
@bot.message_handler(state=MyStates.sub_catalog)
def sub_catalog(message):
    print(btn_back[message.chat.id])
    print(message.text)
    # bot.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=message_to_user[lang[message.chat.id]],reply_markup=get_second_sub_catalog(lang[message.chat.id],message.text)[0])

    btn_back[message.chat.id]['back_sub_catalog'] = (get_sub_catalog(lang[message.chat.id],message.text)[2])
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_second_sub_catalog(lang[message.chat.id],message.text)[0])
    bot.set_state(message.from_user.id, MyStates.in_sub_catalog, message.chat.id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

@bot.message_handler(state=MyStates.in_sub_catalog,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_product(message):
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                     reply_markup=get_back_catalog(lang[message.chat.id], btn_back[message.chat.id]['back_catalog']))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    bot.set_state(message.from_user.id, MyStates.sub_catalog, message.chat.id)
    # btn_back[message.chat.id]['back_catalog'] =''
############################################################sub_catalog






############################################################in_sub_catalog_show
@bot.message_handler(state=MyStates.in_sub_catalog)
def in_sub_catalog_show(message):
    print(message.text)
    if len(get_sub_catalog(lang[message.chat.id],message.text)[1]) == 0:

        print(btn_back[message.chat.id])

        select_user[message.chat.id] = []
        db = SQLite(DATABASE)
        row = db.get_parent_id_from_database(lang[message.chat.id], message.text)
        btn_back[message.chat.id]['back_in_pod_sub_catalog_show'] = row[0][0]


        bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_products(lang[message.chat.id],message.text)[0])
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.set_state(message.from_user.id, MyStates.back_from_products, message.chat.id)

    else:
        print(btn_back[message.chat.id])

        btn_back[message.chat.id]['back_in_sub_catalog_show'] = (get_sub_catalog(lang[message.chat.id], message.text)[2])

        bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_sub_catalog(lang[message.chat.id],message.text)[0])
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.set_state(message.from_user.id, MyStates.in_pod_sub_catalog, message.chat.id)

@bot.message_handler(state=MyStates.in_pod_sub_catalog,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_product(message):

    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                     reply_markup=get_back_catalog(lang[message.chat.id], btn_back[message.chat.id]['back_sub_catalog'] ))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    bot.set_state(message.from_user.id, MyStates.in_sub_catalog, message.chat.id)
############################################################in_sub_catalog_show

@bot.message_handler(state=MyStates.back_from_products,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_products_btn(message):
    if btn_back[message.chat.id]['back_in_pod_sub_catalog_show'] == '':

        bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                         reply_markup=get_back_catalog(lang[message.chat.id],
                                                       btn_back[message.chat.id]['back_in_sub_catalog_show']))
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.set_state(message.from_user.id, MyStates.in_sub_catalog, message.chat.id)

    # Code to be executed if either condition is true
    else:
        bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                         reply_markup=get_sec_back_catalog(lang[message.chat.id], btn_back[message.chat.id]['back_in_pod_sub_catalog_show']))
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.set_state(message.from_user.id, MyStates.in_sub_catalog, message.chat.id)
        btn_back[message.chat.id]['back_in_pod_sub_catalog_show'] = ''



############################################################in_pod_sub_catalog_show
@bot.message_handler(state=MyStates.in_pod_sub_catalog)
def in_pod_sub_catalog_show(message):
    if len(get_sub_catalog(lang[message.chat.id], message.text)[1]) == 0:
        print(btn_back[message.chat.id])
        print('man')
        # btn_back[message.chat.id]['back_from_product'] = (get_sub_catalog(lang[message.chat.id], message.text)[2])
        btn_back[message.chat.id]['back_man_in_sub_catalog_show'] = (get_sub_catalog(lang[message.chat.id], message.text)[2])

        bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_products(lang[message.chat.id],message.text)[0])
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.set_state(message.from_user.id, MyStates.back_from_products, message.chat.id)
    else:
        print('q')
        print(btn_back[message.chat.id])

        btn_back[message.chat.id]['back_in_sub_catalog_show'] = (get_sub_catalog(lang[message.chat.id], message.text)[2])
        bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_sub_catalog(lang[message.chat.id],message.text)[0])
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

        bot.set_state(message.from_user.id, MyStates.in_product, message.chat.id)

@bot.message_handler(state=MyStates.in_product,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_four_to(message):
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                     reply_markup=get_back_catalog(lang[message.chat.id], btn_back[message.chat.id]['back_in_sub_catalog_show'] ))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    bot.set_state(message.from_user.id, MyStates.in_pod_sub_catalog, message.chat.id)

############################################################in_pod_sub_catalog_show







@bot.message_handler(state=MyStates.in_product)
def in_last_product(message):
    select_user[message.chat.id] = []
    db = SQLite(DATABASE)
    row = db.get_parent_id_from_database(lang[message.chat.id],message.text)
    # btn_back[message.chat.id]['back_from_product'] = (get_sub_catalog(lang[message.chat.id], message.text)[2])
    btn_back[message.chat.id]['back_from_product'] = row[0][0]
    select_user[message.chat.id] = []
    # bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
    #                       text=message_to_user[lang[message.chat.id]],
    #                       reply_markup=get_products(lang[message.chat.id], message.text)[0])
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                     reply_markup=get_products(lang[message.chat.id], message.text)[0])
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    bot.set_state(message.from_user.id, MyStates.back_from_products, message.chat.id)

@bot.message_handler(state=MyStates.back_from_products,text = ["⬅️ Ortga","⬅️ Назад"])
def back_from_products_btn(message):
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                     reply_markup=get_back_catalog(lang[message.chat.id], btn_back[message.chat.id]['back_from_product']))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    bot.set_state(message.from_user.id, MyStates.in_pod_sub_catalog, message.chat.id)


@bot.message_handler(state=MyStates.back_from_products)
def products(message):
    select_user[message.chat.id] = []
    basket_to_user[message.chat.id] = message.text
    db = SQLite(DATABASE)
    row = db.select_product_id(lang[message.chat.id],message.text)
    btn_back[message.chat.id]['back_from_basket'] = row[0][0]
    product_name = message.text
    select_user[message.chat.id].append(product_name)
    db = SQLite(DATABASE)
    row = db.select_product_show(lang[message.chat.id], message.text)
    number = row[0][2]
    d = "{:,.0f}".format(number).replace(",", " ")

    try:
        if lang[message.chat.id] =='uz':
            product_caption = f"💻 Mahsulot: {row[0][0]}\n💬 Mahsulot izohi: {row[0][1]}\n💰 Narxi: {d} so'm"
            bot.send_photo(message.chat.id, photo=open(f'{IMAGE}/{row[0][3]}', 'rb'), caption=product_caption,reply_markup=get_number(lang[message.chat.id]))
            bot.send_message(message.chat.id, choose_message[lang[message.chat.id]])
            bot.set_state(message.from_user.id, MyStates.basket, message.chat.id)

        if lang[message.chat.id] =='ru':
            product_caption = f"💻 Название: {row[0][0]}\n💬 Описание: {row[0][1]}\n💰 Цена: {d} so'm"
            bot.send_photo(message.chat.id, photo=open(f'{IMAGE}/{row[0][3]}', 'rb'), caption=product_caption,reply_markup=get_number(lang[message.chat.id]))
            bot.send_message(message.chat.id, choose_message[lang[message.chat.id]])
            bot.set_state(message.from_user.id, MyStates.basket, message.chat.id)

    except Exception as e:
        print(e)




@bot.message_handler(state=MyStates.basket,text = ["⬅️ Ortga","⬅️ Назад"])
def basket_back(message):
    print(btn_back[message.chat.id])
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]],
                     reply_markup=get_last_products(lang[message.chat.id], btn_back[message.chat.id]['back_from_basket']))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    bot.set_state(message.from_user.id, MyStates.back_from_products, message.chat.id)


@bot.message_handler(state=MyStates.basket)
def basket_func(message):
    try:
        db = SQLite(DATABASE)
        count_of_products = message.text
        row = db.select_product_show(lang[message.chat.id],select_user[message.chat.id][0])
        total_price = int(row[0][2]) * int(count_of_products)
        db.insert_baskets(message.chat.id,select_user[message.chat.id][0],count_of_products,row[0][2],total_price)
        bot.send_message(message.chat.id, basket_user[lang[message.chat.id]].format(basket_to_user[message.chat.id]))

        header(message)
    except Exception as e:
        print(e)








#############Complaint#########
@bot.message_handler(state=MyStates.header_menu,text=["🛟 ️Taklif va shikoyatlar", "🛟 ️Предложения и жалобы"])
def complaint(message):
    bot.send_message(message.chat.id, complaint_message[lang[message.chat.id]],reply_markup=get_complaint(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.complaint, message.chat.id)

#############ComplaintVoice#########
@bot.message_handler(state=MyStates.complaint,text=["🎙 Ovozli xabar shaklida", "🎙 В виде голосового сообщения"])
def complaint_voice(message):
    bot.send_message(message.chat.id, complaint_voice_message[lang[message.chat.id]],reply_markup=get_handle_complaint(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.complaint_vocie, message.chat.id)

@bot.message_handler(state=MyStates.complaint_vocie,content_types=['voice'])
def send_voice(message):
    voice_message = message.voice
    file_id = voice_message.file_id
    # Send the voice message to the group
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    silka = message.from_user.username
    chat_id = "6169983011"
    if message.from_user.username == None:
        bot.send_voice(-963466862, file_id, caption=f'*\n\n👤 Telegram account*: {mention}', parse_mode="Markdown")
    else:
        bot.send_voice(-963466862, file_id, caption="\n\n👤 <b>Telegram account: @</b>" + silka, parse_mode="HTML")

    bot.send_message(message.chat.id, handle_message[lang[message.chat.id]],reply_markup=get_handle_complaint(lang[message.chat.id]))
    header(message)

###############complaint_vocie#####
@bot.message_handler(state=MyStates.complaint_vocie,text=["⬅️ Ortga", "⬅️ Назад"])
def backto(message):
    header(message)



################


@bot.message_handler(state=MyStates.complaint,text=["⬅️ Ortga", "⬅️ Назад"])
def backto(message):
    header(message)
#############Complaint Handy style#########
@bot.message_handler(state=MyStates.complaint,text=["✍️ Yozma xabar shaklida", "✍️ В виде письменного сообщения"])
def complaint_hand(message):
    bot.send_message(message.chat.id, complaint_handle_message[lang[message.chat.id]],reply_markup=get_handle_complaint(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.complaint_handle_st, message.chat.id)

@bot.message_handler(state=MyStates.complaint_handle_st,text=["⬅️ Ortga", "⬅️ Назад"])
def back_from_complaint(message):
    header(message)

#############Complaint Handy style Send to group#########
@bot.message_handler(state=MyStates.complaint_handle_st)
def send_hand_complaint(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    fikr_rus_in = message.text
    silka = message.from_user.username
    if message.from_user.username == None:
        bot.send_message(-963466862, fikr_rus_in + f'*\n\n👤 Telegram account*: {mention}', parse_mode="Markdown")
    else:
        bot.send_message(-963466862, fikr_rus_in + "\n\n👤 <b>Telegram account: @</b>" + silka, parse_mode="HTML")

    bot.send_message(message.chat.id, handle_message[lang[message.chat.id]],reply_markup=get_handle_complaint(lang[message.chat.id]))
    header(message)



######################SocialMedia
@bot.message_handler(state=MyStates.header_menu,text=["🔆 Ijtimoiy tarmoqlar", "🔆 Социальные сети"])
def social_media(message):
    bot.send_message(message.chat.id, ijtimoiy_tarmoqlar_message[lang[message.chat.id]],
                     reply_markup=get_social_media(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.social_media_st, message.chat.id)

@bot.message_handler(state=MyStates.social_media_st,text=["⬅️ Ortga", "⬅️ Назад"])
def back_to_header(message):
    header(message)

@bot.message_handler(state=MyStates.social_media_st,text=["📱 Mobil telefonlar bo'limi", "📱 Телефонный отдел"])
def mobile_social(message):
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("Telegram", url="https://t.me/orzutech_group")
    btn2 = InlineKeyboardButton("Instagram",
                                      url="https://instagram.com/orzutech?igshid=MzRlODBiNWFlZA==")
    btn3 = InlineKeyboardButton("Web site", url="https://orzutech.uz/")

    btn4 = InlineKeyboardButton("Facebook", url="https://www.facebook.com/orzutech.bukhara?mibextid=ZbWKwL")

    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, social_media_message[lang[message.chat.id]], reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)
    header(message)

@bot.message_handler(state=MyStates.social_media_st,text=["🖥 Kompyuterlar bo'limi", "🖥Компьютерный отдел"])
def komp_social(message):
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("Telegram", url="https://t.me/orzutech_computers")
    btn2 = InlineKeyboardButton("Instagram",
                                      url="https://instagram.com/orzutech_computers?igshid=Y2IzZGU1MTFhOQ==")

    btn3 = InlineKeyboardButton("Web site", url="https://orzutech.uz/")
    btn4 = InlineKeyboardButton("Facebook", url="https://www.facebook.com/orzutech.bukhara?mibextid=ZbWKwL")

    markup.add(btn1, btn2, btn3,btn4)
    bot.send_message(message.chat.id, social_media_message[lang[message.chat.id]], reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)
    header(message)

@bot.message_handler(state=MyStates.social_media_st,text=["🎥 Videokuzatuv bo'limi", "🎥Отдел видеонаблюдение"])
def security_social(message):
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("Telegram", url="https://t.me/orzutech_camera")
    btn2 = InlineKeyboardButton("Instagram",
                                      url="https://instagram.com/orzutech_camera?igshid=Y2IzZGU1MTFhOQ==")

    btn4 = InlineKeyboardButton("Facebook", url="https://www.facebook.com/orzutech.bukhara?mibextid=ZbWKwL")
    btn3 = InlineKeyboardButton("Web site", url="https://orzutech.uz/")

    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, social_media_message[lang[message.chat.id]], reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)
    header(message)



######################Location
@bot.message_handler(state=MyStates.header_menu,text=["🚩 Do'kon Lokatsiyasi", "🚩 Расположение Магазина"])
def location(message):
    bot.send_location(message.from_user.id, 39.762905, 64.429983)
    bot.send_message(message.chat.id, send_location_message[lang[message.chat.id]])
    bot.delete_state(message.from_user.id, message.chat.id)

    header(message)

############Kontakt
@bot.message_handler(state=MyStates.header_menu, text=["📞️ Kontaktlar","📞️ Контакты"])
def user_kontakt(message):
    bot.send_message(message.chat.id, kontakt_message[lang[message.chat.id]])
    bot.delete_state(message.from_user.id, message.chat.id)
    header(message)


#############Settings
@bot.message_handler(state=MyStates.header_menu,text=["⚙️ Sozlamalar", "⚙️ Настройки"])
def user_setting(message):
    bot.send_message(message.chat.id, message_to_user[lang[message.chat.id]], reply_markup=get_sozlamalar(lang[message.chat.id]))
    bot.set_state(message.from_user.id, MyStates.settings, message.chat.id)

@bot.message_handler(state=MyStates.settings,text=["⬅️ Ortga", "⬅️ Назад"])
def back_from_settings(message):
    header(message)

@bot.message_handler(state=MyStates.settings,text=["🌐 Tilni tanlash", "🌐 Выбрать язык"])
def user_language(message):
    bot.send_message(message.chat.id, "Iltimos, tilni tanlang ⬇️ : Пожалуйста, выберите язык ⬇️",reply_markup=get_lang())
    bot.set_state(message.from_user.id, MyStates.update_language, message.chat.id)


@bot.message_handler(state=MyStates.update_language,text=["🇺🇿O'zbek tili", "🇷🇺Pусский язык"])
def update_til(message):
    global lang
    if message.text in lang_msg:
        if message.text == lang_msg[1]:
            lang[message.chat.id] = 'ru'
            db = SQLite(DATABASE)
            db.update_data_lang("ru", message.chat.id)
            header(message)
        if message.text == lang_msg[0]:
            lang[message.chat.id] = 'uz'
            db = SQLite(DATABASE)
            db.update_data_lang("uz", message.chat.id)
            header(message)

@bot.message_handler(commands=['orzu'])
def admin(message):
    bot.send_message(message.chat.id, "Quyidagilardan birini tanlang 👇🏻",reply_markup=get_admin_btn())
    bot.set_state(message.from_user.id, MyStates.admin, message.chat.id)

@bot.message_handler(state=MyStates.admin,text="Tugma bilan xabar yuborish")
def send_with_btn(message):
    bot.send_message(message.chat.id,"Quyidagilardan birini tanlang 👇🏻", reply_markup=get_admin_btn_inline())
    bot.set_state(message.from_user.id, MyStates.admin_send_btn, message.chat.id)

@bot.message_handler(state=MyStates.admin_send_btn,text="📹 Tugmali Video va Text")
def send_video_inline(message):
    bot.send_message(message.chat.id, "📹 Video tagidagi gapi bilan yuboring yoki faqat videoni o'zini yuboring",reply_markup=back())
    bot.set_state(message.from_user.id, MyStates.admin_send_video_btn, message.chat.id)

@bot.message_handler(state=MyStates.admin_send_video_btn,text = "⬅️ Ortga")
def back_video(message):
    send_with_btn(message)



@bot.message_handler(state=MyStates.admin_send_video_btn,content_types=['video'])
def ask_video(message):
    if message.video:
        # Save the received video and directly proceed to asking for the button name
        state.caption = message.caption
        state.video_id = message.video.file_id
        bot.send_message(message.chat.id, "Iltimos tugma nomini yuboring")
        bot.register_next_step_handler(message, ask_button_name)
    else:
        # No video received, ask again
        bot.send_message(message.chat.id, "Iltimos video yuboring")
        bot.register_next_step_handler(message, ask_video)

@bot.message_handler(state=MyStates.admin_send_btn,text="🖼 Tugmali Rasm va Text")
def send_inline_photo(message):
    bot.send_message(message.chat.id, "🖼 Rasmni tagidagi gapi bilan yuboring yoki faqat rasmni o'zini yuboring",reply_markup=back())
    bot.set_state(message.from_user.id, MyStates.admin_send_photo_btn, message.chat.id)



@bot.message_handler(state=MyStates.admin_send_photo_btn,text = "⬅️ Ortga")
def back_inline_photo(message):
    send_with_btn(message)





@bot.message_handler(state=MyStates.admin_send_photo_btn,content_types=['photo'])
def ask_photo(message):
    if message.photo:
        state.caption = message.caption
        # Save the received photo and ask for the caption
        state.photo_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, "Iltimos tugma nomini yuboring")
        bot.register_next_step_handler(message, ask_button_name)
    else:
        # No photo received, ask again
        bot.send_message(message.chat.id, "Iltimos rasm yuboring")
        bot.register_next_step_handler(message, ask_photo)




def ask_button_name(message):
    # Save the button name and ask for the button URL
    button_name = message.text
    bot.send_message(message.chat.id, "Iltimos tugma uchun Url yuboring")
    bot.register_next_step_handler(message, ask_button_url, button_name)

def ask_button_url(message, button_name):
    # Save the button URL and add the button to the list
    button_url = message.text
    state.buttons.append((button_name, button_url))

    # Ask whether to add another button or finish
    reply_markup = create_reply_markup()
    bot.send_message(message.chat.id, "Tugma qo'shildi.Boshqa tugma qo'shasizmi yoki Tugmalarni jo'natamizmi?", reply_markup=reply_markup)

# Helper function to create the reply markup with buttons
def create_reply_markup():
    buttons = [KeyboardButton("Yana Tugma qo'shish"), KeyboardButton("Tugmalarni jo'natish")]
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

# Handler for the "Add another button" button
@bot.message_handler(func=lambda message: message.text =="Yana Tugma qo'shish")
def add_another_button(message):
    # Ask for the button name and URL for the additional button
    bot.send_message(message.chat.id, "Iltimos tugma nomini yuboring.")
    bot.register_next_step_handler(message, ask_button_name)

# Handler for the "That's it" button
@bot.message_handler(func=lambda message: message.text == "Tugmalarni jo'natish")
def thats_it_button(message):
    if not state.buttons:
        # No buttons added, ask again
        bot.send_message(message.chat.id, "Bironta ham tugma qo'shilmadi.Iltimos bironta tugma qo'shing!")
        return

    # Create inline keyboard with the buttons
    keyboard = InlineKeyboardMarkup()
    for button in state.buttons:
        button_name, button_url = button
        keyboard.add(InlineKeyboardButton(button_name, url=button_url))
    if state.photo_id:
        if state.caption is None:
            bot.send_photo(message.chat.id, state.photo_id,  reply_markup=keyboard)
        else:
            bot.send_photo(message.chat.id, state.photo_id, caption=state.caption, reply_markup=keyboard)
    elif state.video_id:
        print('video')
        if state.caption is None:
            bot.send_video(message.chat.id, state.video_id, reply_markup=keyboard)
        else:
            bot.send_video(message.chat.id, state.video_id, caption=state.caption, reply_markup=keyboard)
    state.buttons = []
    admin(message)
# Start the bot


@bot.message_handler(state=MyStates.admin_send_btn,text="⬅️ Ortga")
def back_admin_btn(message):
    admin(message)


@bot.message_handler(state=MyStates.admin_send,text="⬅️ Ortga")
def back_admin_header(message):
    admin(message)



@bot.message_handler(state=MyStates.admin,text="👁 Foydalanuvchilar sonini ko'rish")
def see_user(message):
    db = SQLite(DATABASE)
    db.calaculate_sum_user()
    bot.send_message(message.chat.id, f"👤 Jami foydalanuvchilar soni: <b>{db.calaculate_sum_user()} ta</b>", reply_markup=get_admin_btn())
    admin(message)
@bot.message_handler(state=MyStates.admin,text="Tugmasiz xabar yuborish")
def admin_send_message(message):
    bot.send_message(message.chat.id,"Quyidagilardan birini tanlang 👇🏻", reply_markup=get_admin_send())
    bot.set_state(message.from_user.id, MyStates.admin_send, message.chat.id)

@bot.message_handler(state=MyStates.admin_send,text="📹 Video va Text")
def admin_send_video(message):
    bot.send_message(message.chat.id, "📹 Video tagidagi gapi bilan yuboring yoki faqat videoni o'zini yuboring",reply_markup=back())
    bot.set_state(message.from_user.id, MyStates.video, message.chat.id)


@bot.message_handler(state=MyStates.video,content_types=['video'])
def send_video_from_admin(message):
    video = None
    if message.video:
        video = message.video.file_id
        # Retrieve the admin's caption
    caption = message.caption
    # Send the message to each user
    db = SQLite(DATABASE)
    rows = db.send_user_message()


    # Send the message to each user
    for user_id in rows:
        try:
            if video:
                bot.send_video(user_id[0], video, caption=caption)
            else:
                bot.send_message(user_id[0], caption)
        except Exception as e:
            print(e)
    admin(message)

#
@bot.message_handler(state=MyStates.video,text="⬅️ Ortga")
def back_admin_video(message):
    admin_send_message(message)


@bot.message_handler(state=MyStates.admin_send,text="🖼 Rasm va Text")
def admin_send_photo(message):
    bot.send_message(message.chat.id, "🖼 Rasmni tagidagi gapi bilan yuboring yoki faqat rasmni o'zini yuboring",reply_markup=back())
    bot.set_state(message.from_user.id, MyStates.photo, message.chat.id)

#
@bot.message_handler(state=MyStates.photo,text="⬅️ Ortga")
def back_admin_text(message):
    admin_send_message(message)


@bot.message_handler(state=MyStates.photo,content_types=['photo'])
def send_photo_from_admin(message):
    photo = None
    if message.photo:
        photo = message.photo[-1].file_id
    caption = message.caption
    # Send the message to each user
    db = SQLite(DATABASE)
    rows = db.send_user_message()
    for user_id in rows:
        try:
            if photo:
                bot.send_photo(user_id[0], photo, caption=caption)
            else:
                bot.send_message(user_id[0], caption)
        except Exception as e:
            print(e)
    admin(message)




@bot.message_handler(state=MyStates.admin_send,text="✍ Text")
def admin_text(message):
    bot.send_message(message.chat.id, "✍ Text yuboring",reply_markup=back())
    bot.set_state(message.from_user.id, MyStates.text_admin, message.chat.id)



@bot.message_handler(state=MyStates.text_admin,text="⬅️ Ortga")
def back_admin_text(message):
    admin_send_message(message)


@bot.message_handler(state=MyStates.text_admin)
def send_text_from_admin(message):
    sms = message.text
    db = SQLite(DATABASE)
    rows = db.send_user_message()
    for i in rows:
        try:
            bot.send_message(i[0], sms,parse_mode="Markdown")
        except Exception as e:
            print(e)
    admin(message)












bot.add_custom_filter(custom_filters.TextMatchFilter())
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(custom_filters.ChatFilter())
# bot.infinity_polling()