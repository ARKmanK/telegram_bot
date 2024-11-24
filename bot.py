import telebot
import random
import os


from telebot import types
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))


class Cart:
    def __init__(self):
        self.cart = {}     
        self.order_number = random.randint(1000, 9999) 
        self.order = False

    def add_stuff(self, item):
        if item not in self.cart:
            self.cart[item] = 1

    def remove_stuff(self, item):
        if item in self.cart:
            del self.cart[item]

    def edit_quantity(self, item, quantity):
        self.cart[item] = quantity

    def show_cart(self):
        return self.cart

cart = Cart()

#------------------------------Команды бота-----------------------------#
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Создать новый заказ')
    item2 = types.KeyboardButton('Добавить товар')
    item3 = types.KeyboardButton('Посмотреть корзину')
    item4 = types.KeyboardButton('Оформить заказ')

    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id, f"Здравствуй {message.from_user.first_name} {message.from_user.last_name}, давай соберем тебе корзину покупок")

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == 'Создать новый заказ':
        new_order(message)
    elif message.text == 'Добавить товар':
        add_stuff(message)
    elif message.text == 'Посмотреть корзину':
        show_cart(message)
    elif message.text == 'Оформить заказ':
        confirm(message)









#@bot.message_handler(commands=['new_order'])
def new_order(message):
    if len(cart.cart) > 0 and cart.order == True:
        bot.send_message(message.chat.id, 'Вы уверены, что хотите создать новый заказ? В корзине есть товары')
        cart.order = False
        return
    cart.order = True
    cart.cart = {}
    cart.order_number = random.randint(1000, 9999)
    bot.send_message(message.chat.id, f'Создан новый заказ №{cart.order_number}')

"""@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Здравствуй {message.from_user.first_name} {message.from_user.last_name}, давай соберем тебе корзину покупок\nИспользуй '/' для ввода команд")
"""
#@bot.message_handler(commands=['add_stuff'])
def add_stuff(message):
    if cart.order:
        bot.send_message(message.chat.id, 'Введите список товаров')
        bot.register_next_step_handler(message, get_stuff_list)
    else:
        bot.send_message(message.chat.id, 'Создайте новый заказ')

@bot.message_handler(commands=['edit_quantity'])
def edit_quantity(message):
    if cart.cart:
        bot.send_message(message.chat.id, 'Количество какого товара вы желаете изменить?')
        show_cart(message)
        bot.register_next_step_handler(message, get_stuff_info, mode='quantity')
    else:
        bot.send_message(message.chat.id, 'Ваша корзина пуста')

@bot.message_handler(commands=['show_cart'])
def show_cart(message):
    cart_items = cart.show_cart().items()
    cart_str = '\n'.join(f"{key}: {value} шт." for key, value in cart_items)
    if len(cart_items) > 0:
        bot.send_message(message.chat.id, f'Ваши товары:\n{cart_str}')        
    else:
        bot.send_message(message.chat.id, 'Ваша корзина пуста')

@bot.message_handler(commands=['remove_stuff'])
def remove_stuff(message):
    if cart.cart:
        show_cart(message)
        bot.send_message(message.chat.id, 'Какой товар вы хотите убрать из корзины?')
        bot.register_next_step_handler(message, get_stuff_info, mode='remove')
    else:
        bot.send_message(message.chat.id, 'Ваша корзина пуста')

@bot.message_handler(commands=['confirm'])
def confirm(message, mode=None): 
    """if cart.cart:   
        if mode == 'verification':
            bot.send_message(message.chat.id, f'Для подтверждения заказа введите "confirm{cart.order_number}"')
            bot.register_next_step_handler(message, check_verification)
        else:
            bot.send_message(message.chat.id, f'Ваш заказ готов!\nДля подтверждения заказа введите "confirm{cart.order_number}"')
            bot.register_next_step_handler(message, check_verification)
    else:
        bot.send_message(message.chat.id, 'Ваша корзина пуста')"""
    if cart.cart:   
        if mode == 'verification':
            keyboard = types.ReplyKeyboardMarkup(row_width=1)
            keyboard.add(types.KeyboardButton('Отмена'), types.KeyboardButton('Подтвердить'))
            bot.send_message(message.chat.id, 'Для подтверждения заказа', reply_markup=keyboard)
            bot.register_next_step_handler(message, check_verification)
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1)
            keyboard.add(types.KeyboardButton('Отмена'), types.KeyboardButton('Подтвердить'))
            bot.send_message(message.chat.id, 'Ваш заказ готов!', reply_markup=keyboard)
            bot.register_next_step_handler(message, check_verification)
    else:
        bot.send_message(message.chat.id, 'Ваша корзина пуста')




#----------------------------Основные функции----------------------------#
def get_stuff_list(message):
    items = [item.strip().lower().title() for item in message.text.split(',') if item != '']
    if len(items) == 1:
        if items[0] in cart.cart:
            bot.send_message(message.chat.id, 'Данный товар уже есть в корзине, введите что-нибудь другое')
            bot.register_next_step_handler(message, get_stuff_list)
        else:
            cart.add_stuff(items[0])
            bot.send_message(message.chat.id, 'Товар добавлен в корзину')
    else:
        for item in items:       
            cart.add_stuff(item)
        bot.send_message(message.chat.id, 'Товары добавлены в корзину')

def get_stuff_info(message, mode=None):
    item_name = message.text
    if mode == 'quantity':
        if item_name.title() not in cart.cart:
            bot.send_message(message.chat.id, 'Данного товара нет в корзине')
            edit_quantity(message)
        else:
            bot.send_message(message.chat.id, 'На какое количество вы желаете изменить?')
            bot.register_next_step_handler(message, get_new_quantity, item_name.title())
    elif mode == 'remove':
        if item_name.title() not in cart.cart:
            bot.send_message(message.chat.id, 'Данного товара нет в корзине')
            remove_stuff(message)
        else:
            cart.remove_stuff(item_name.title())
            bot.send_message(message.chat.id, 'Товар удален из корзины')

def get_new_quantity(message, item_name):
    new_quantity = int(message.text)
    cart.edit_quantity(item_name, new_quantity)
    bot.send_message(message.chat.id, 'Количество товара изменено')
    show_cart(message)

def check_verification(message):
    if message.text == f'confirm{cart.order_number}':
        bot.send_message(message.chat.id, f'Ваш заказ успешно размещен!')
    else:
        bot.send_message(message.chat.id, f'Ошибка подтверждения.')
        confirm(message, mode='verification')


bot.polling(none_stop=True)




"""
отменить/подтвердить (кнопки)
фото подтверждения оплаты
"""