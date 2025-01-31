import telebot
import logging
import json
from telebot import types

from config import api_token

TOKEN = api_token

bot = telebot.TeleBot(TOKEN)

menu_items = [
        {"name": "Грибной суп", "price": "450 руб.", "photo": "mushroom_soup.png"},
        {"name": "Салат Цезарь", "price": "550 руб.", "photo": "caesar.png"},
        {"name": "Утка с апельсинами", "price": "700 руб.", "photo": "duck_orange.png"},
        {"name": "Бефстроганов", "price": "650 руб.", "photo": "stroganoff.png"},
        {"name": "Ризотто", "price": "500 руб.", "photo": "risotto.png"},
        {"name": "Тирамису", "price": "400 руб.", "photo": "tiramisu.png"},
        {"name": "Блины", "price": "300 руб.", "photo": "pancakes.png"},
        {"name": "Паста Карбонара", "price": "550 руб.", "photo": "carbonara.png"},
        {"name": "Гаспачо", "price": "350 руб.", "photo": "gazpacho.png"},
        {"name": "Фалафель", "price": "400 руб.", "photo": "falafel.png"}

]

ITEMS_PER_PAGE = 4

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Это твой третий бот! Перед тем как начать, используй команду /add_info", reply_markup=button_menu())

@bot.message_handler(commands=["add_info"])
def handle_info(message):
    bot.send_message(message.chat.id, "Введите имя и номер телефона через запятую")
    name = message.text
    phone = message.text
    id = message.chat.id

    bot.register_next_step_handler_by_chat_id(message.chat.id, info, name, phone, id)

def info(message, name, phone, id):
    # Чтение существующих данных из файл
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"clients": []}

    if name == "/add_info":
        name = message.text.split(", ")[0]
        phone = message.text.split(", ")[1]

    # Добавление новой записи
    new_info = {"id": str(id), "name": name, "phone": phone, "address": ...}
    data["clients"] = new_info

    bot.send_message(message.chat.id, "Спасибо за данные")

    # Запись обновленных данных в файл
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def button_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_button = types.KeyboardButton("Меню")
    cart_button = types.KeyboardButton("Корзина")
    order_button = types.KeyboardButton("Заказать")

    markup.add(menu_button, cart_button, order_button)
    return markup

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == "Меню":
        bot.reply_to(message, "Меню")
        bot.send_message(message.chat.id, "Основное меню", reply_markup=generate_menu_markup())

    if message.text == "Корзина":
        items_in_cart = get_cart(message.chat.id)

        markup = types.InlineKeyboardMarkup()

        for item in items_in_cart:
            minus_button = types.InlineKeyboardButton("-", callback_data=f"minus_{item[0]}")
            name_button = types.InlineKeyboardButton(f"{item[0]} x{item[1]}", callback_data=f"name_{item}")
            plus_button = types.InlineKeyboardButton("+", callback_data=f"plus_{item[0]}")

            markup.add(minus_button, name_button, plus_button)
        
        bot.send_message(message.chat.id, "Корзина:", reply_markup=markup)
    
    if message.text == "Заказать":
        items_in_cart = get_cart(message.chat.id)
        mes = "\n"
        for item in items_in_cart:
            mes += f"✨{item[0]} x{item[1]} \n"
        bot.send_message(message.chat.id, f"Ваша корзина: {mes}")
        bot.send_message(message.chat.id, "Подтвердите правильность заказа", reply_markup=order_menu())

    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Заказ не принят в работу. Вы можете изменить заказ", reply_markup=button_menu())
    if message.text == "Подтвердить":
        bot.send_message(message.chat.id, "Укажите адрес, куда доставить еду(введите текстом(сначала широта, потом долгота, через запятую) или геометкой)")

        bot.register_next_step_handler_by_chat_id(message.chat.id, create_order)

def create_order(message):
    # Чтение существующих данных из файл
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"clients": []}

    if message.content_type == 'text':
        coord = message.text
        clients = data.get("clients", [])
        for client in clients:
            if client["id"] == str(message.chat.id):
                client["address"] = coord

        bot.send_message(message.chat.id, f"Вы выбрали адрес: {coord}")
        bot.send_message(message.chat.id, f"Стоимость заказа: {calculate_cart_total(message.chat.id)}")
        bot.send_message(message.chat.id, "Доступна только оплата наличными курьеру")
        bot.send_message(message.chat.id, "Заказ принят в работу", reply_markup=button_menu())
        # calculate_cart_total(message.chat.id)

    
    elif message.content_type == 'location' or message.content_type == 'venue':
        coord1 = message.location.latitude
        coord2 = message.location.longitude
        clients = data.get("clients", [])
        for client in clients:
            if client["id"] == str(message.chat.id):
                client["address"] = coord1, coord2
        
        bot.send_message(message.chat.id, f"Вы выбрали адрес: {coord1}, {coord2}")
        bot.send_message(message.chat.id, f"Стоимость заказа: {calculate_cart_total(message.chat.id)}")
        bot.send_message(message.chat.id, "Доступна только оплата наличными курьеру")
        bot.send_message(message.chat.id, "Заказ принят в работу", reply_markup=button_menu())

# Запись обновленных данных в файл
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def calculate_cart_total(id):
    # Чтение существующих данных из файл
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"clients": []}

    total_price = 0

    clients = data.get("clients", [])
    for client in clients:
        if client["id"] == str(id):
            for item in menu_items:
                for cart_item in client["cart"]:
                    if cart_item[0] == item["name"]:
                        total_price += int(item["price"].split(" ")[0]) * int(cart_item[1])

    # Запись обновленных данных в файл
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return total_price
    
def order_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    confirm_button = types.KeyboardButton("Подтвердить")
    deny_button = types.KeyboardButton("Отмена")

    markup.add(confirm_button, deny_button)
    return markup

def generate_menu_markup(page=0):
    keyboard = telebot.types.InlineKeyboardMarkup()

    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    for button_text in menu_items[start_index:end_index]:
        callback_data = f"item_{menu_items.index(button_text)}"
        button = telebot.types.InlineKeyboardButton(text=f"{button_text["name"]}", callback_data=callback_data)
        keyboard.add(button)

    if page > 0:
        keyboard.add(types.InlineKeyboardButton(text="<<", callback_data=f"page_{page-1}"))
    if end_index < len(menu_items):
        keyboard.add(types.InlineKeyboardButton(text=">>", callback_data=f"page_{page+1}"))

    return keyboard
    
@bot.callback_query_handler(func = lambda call: True)
def querry_handler(call):
    # Чтение существующих данных из файл
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"clients": []}

    if call.data.startswith("page_"):
        text, page = call.data.split("_")
        markup = generate_menu_markup(int(page))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбор элемента:", reply_markup = markup)
    elif call.data.startswith("plus_"):
        text, item_index = call.data.split("_")
        
        clients = data.get("clients", [])
        for client in clients:
            if client["id"] == str(call.message.chat.id):
                food_name = call.data.split("_")[1]
                for cart_item in client["cart"]:
                    if cart_item[0] == food_name:
                        cart_item[1] += 1
                        break
                else:
                    client["cart"].append([food_name, 1])
    
    elif call.data.startswith("minus_"):
        clients = data.get("clients", [])
        for client in clients:
            if client["id"] == str(call.message.chat.id):
                food_name = call.data.split("_")[1]
                for food_item in client["cart"]:
                    if food_item[0] == food_name:
                        food_item[1] -= 1
                        if food_item[1] == 0:
                            client["cart"].remove(food_item)
    
    elif call.data.startswith("item_"):
        bot.send_message(call.message.chat.id, text=f"{menu_items[int(call.data.split("_")[1])]["name"]} добавлено в заказ. Если хотите увеличить количество позиций, зайдите во вкладку Корзина")
        clients = data.get("clients", [])
        for client in clients:
            if client["id"] == str(call.message.chat.id):
                client["cart"].append([menu_items[int(call.data.split("_")[1])]["name"], 1])

    # Запись обновленных данных в файл
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_cart(client_id):
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    clients = data.get("clients", [])
    for client in clients:
        if client.get("id") == str(client_id):
            return client.get("cart", [])
            
        
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Начинаем работу бота")

    bot.polling(non_stop=True)