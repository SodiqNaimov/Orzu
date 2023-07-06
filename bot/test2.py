import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Create an instance of the bot with your Telegram Bot token
bot = telebot.TeleBot('6135723640:AAHz_IeTR7fllosOx-o9IEUYGci5ZnDJuf8')

# ConversationState class to store the conversation state
class ConversationState:
    def __init__(self):
        self.photo_id = None
        self.caption = None
        self.buttons = []

state = ConversationState()

# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalomu alaykum! Welcome to the admin panel.")
    send_photo(message)

# Handler for the "Photo" button
@bot.message_handler(func=lambda message: message.text == 'Photo')
def send_photo(message):
    # Ask for photo
    bot.send_message(message.chat.id, "Please send the photo.")
    bot.register_next_step_handler(message, ask_photo)

def ask_photo(message):
    if message.photo:
        # Save the received photo and directly proceed to asking for the button name
        state.photo_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, "Please enter the button name.")
        bot.register_next_step_handler(message, ask_button_name)
    else:
        # No photo received, ask again
        bot.send_message(message.chat.id, "No photo received. Please send the photo.")
        bot.register_next_step_handler(message, ask_photo)

def ask_button_name(message):
    # Save the button name and ask for the button URL
    button_name = message.text
    bot.send_message(message.chat.id, "Please enter the button URL.")
    bot.register_next_step_handler(message, ask_button_url, button_name)

def ask_button_url(message, button_name):
    # Save the button URL and add the button to the list
    button_url = message.text
    state.buttons.append((button_name, button_url))

    # Ask whether to add another button or finish
    reply_markup = create_reply_markup()
    bot.send_message(message.chat.id, "Button added. Add another button or finish?", reply_markup=reply_markup)

# Helper function to create the reply markup with buttons
def create_reply_markup():
    buttons = [KeyboardButton("Add another button"), KeyboardButton("That's it")]
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)

# Handler for the "Add another button" button
@bot.message_handler(func=lambda message: message.text == 'Add another button')
def add_another_button(message):
    # Ask for the button name and URL for the additional button
    bot.send_message(message.chat.id, "Please enter the button name.")
    bot.register_next_step_handler(message, ask_button_name)

# Handler for the "That's it" button
@bot.message_handler(func=lambda message: message.text == "That's it")
def thats_it_button(message):
    if not state.buttons:
        # No buttons added, ask again
        bot.send_message(message.chat.id, "No buttons added. Please add at least one button.")
        return

    # Create inline keyboard with the buttons
    keyboard = InlineKeyboardMarkup()
    for button in state.buttons:
        button_name, button_url = button
        keyboard.add(InlineKeyboardButton(button_name, url=button_url))

    # Send the photo with caption and the inline keyboard
    bot.send_photo(message.chat.id, state.photo_id, caption=state.caption, reply_markup=keyboard)

# Start the bot
bot.polling()
