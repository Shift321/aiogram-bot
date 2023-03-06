from datetime import date
import datetime
from aiogram import Bot, executor, Dispatcher
from aiogram.types import Message

from database.db import Base, engine, session
from handlers.handlers import register, admin, food, post_menu, time_to_pay_handler, wash_clothes_handler, \
    want_to_add_wish, list_of_wish, delete_user_handler, add_cleaning_handler, when_to_eat_handler, \
    change_text_cleaning_handler, get_feed_back_handler, show_who_eating_for_week_handler

from models.models import User, Menu, Washes, Food, State, Cleaning, FeedBack
from utils.messages import messages, command_list, admin_command_list, meal_text
from utils.utils import logging_tg, is_register, check_week_day, make_state

bot = Bot("5888170225:AAEN6YCV3hBD6G54Kb9tHuDeRajpY_Uicug")
dispatcher = Dispatcher(bot)
Base.metadata.create_all(engine)


@dispatcher.message_handler(commands=['start'])
async def hello(message: Message):
    logging_tg(message.chat.id, message)
    make_state(message.chat.id, "start")
    await bot.send_message(message.chat.id, messages["hello_message_collibring"])
    await bot.send_message(message.chat.id, command_list)


@dispatcher.message_handler(commands=['send_message_to_all'])
async def send_to_all(message: Message):
    all_eat = session.query(Food).all()
    for i in all_eat:
        user = session.query(User.id == i.user_id).all()
        await bot.send_message(user[0].telegram_id,
                               "Привет! Перезапишись пожалуйста на питанеие я произвел технические работы ,теперь все должно работать хорошо команда /meal. Если после перезаписи бот не написал готово напиши об этом пожалуйста сюда @shift123(Саша)")
    await bot.send_message(message.chat.id, "Готово")


@dispatcher.message_handler(commands=['meal'])
async def when_to_eat(message: Message):
    logging_tg(message.chat.id, message)
    make_state(message.chat.id, "meal")
    await bot.send_message(message.chat.id, meal_text)


@dispatcher.message_handler(commands=['pay'])
async def pay(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        make_state(message.chat.id, "pay")
        await bot.send_message(message.chat.id,
                               "Оплату за жильё, питание, разбитую посуду и мероприятия можно перевести по счёту GE40BG0000000537661778 Daria Marshalkina")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['show_users'])
async def show_users(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        await bot.send_message(message.chat.id, messages['not_registered'])
    else:
        if not user[0].is_admin:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")
        else:
            users = session.query(User).order_by("room_number").all()
            text = ""
            for user in users:
                text += f"комната:{user.room_number} Имя:{user.name}\n"
            await bot.send_message(message.chat.id, text)


@dispatcher.message_handler(commands=['add_cleaning'])
async def add_cleaning(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        user = session.query(User).filter(User.telegram_id == message.chat.id, User.is_admin == True).all()
        if len(user) != 0:
            await bot.send_message(message.chat.id,
                                   "Введите день недели и номер комнаты для уборки")
            make_state(message.chat.id, "add_cleaning")
        else:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['show_cleaning'])
async def show_cleanings(message: Message):
    logging_tg(message.chat.id, message)
    now_day = datetime.date.today() + datetime.timedelta(days=1)
    weekday = now_day.strftime("%A")
    if is_register(message):
        cleanings = session.query(Cleaning).filter(Cleaning.week_day == check_week_day(weekday)).all()
        text_to_send = "Просьбы об уборке сегодня:\n\n"
        if len(cleanings) == 0:
            text_to_send = "На сегодня нет уборок"
        else:
            for cleaning in cleanings:
                for room_number in cleaning.room_number.split(","):
                    users = session.query(User).filter(User.room_number == room_number).all()
                    for i in users:
                        if i.cleaning_prefers is not None:
                            text_to_send += f"Комната: {room_number} предпочтения:{i.cleaning_prefers}\n"
                            break
                        else:
                            text_to_send += f"Комната: {room_number} предпочтений нет\n"
        await bot.send_message(message.chat.id, text_to_send)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['/unadmin'])
async def un_admin(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        await bot.send_message(message.chat.id, messages['not_registered'])
    else:
        user[0].is_admin = False
        session.flush()
        session.commit()
        await bot.send_message(message.chat.id, "unadmined")


@dispatcher.message_handler(commands=['delete_user'])
async def delete_user(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        await bot.send_message(message.chat.id, messages['not_registered'])
    else:
        if user[0].is_admin:
            make_state(message.chat.id, "delete_user")
            await bot.send_message(message.chat.id,
                                   "Введите имя и номер комнаты юзера ,которого хотите удалить через пробел")
        else:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")


@dispatcher.message_handler(commands=['wash_clothes'])
async def wash_clothes(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        make_state(message.chat.id, "wash_cloth")
        washes = session.query(Washes).filter(Washes.date == date.today()).order_by('time_start')
        text = ""
        for wash in washes:
            time_start = str(wash.time_start)[:5]
            time_end = str(wash.time_end)[:5]
            text += f"{wash.name} {time_start}-{time_end} ДАТА СТИРКИ:{wash.date}" + "\n"
        text += "Введите время желаемой стирки в формате 15:00-16:00 "
        await bot.send_message(message.chat.id, text)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['admin'])
async def become_admin(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        make_state(message.chat.id, "admin")
        await bot.send_message(message.chat.id, "Введите пароль , его можно получить у Даши🤔")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['commands'])
async def become_admin(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        await bot.send_message(message.chat.id, command_list)
    else:
        if user[0].is_admin:
            await bot.send_message(message.chat.id, admin_command_list)
        else:
            await bot.send_message(message.chat.id, command_list)


@dispatcher.message_handler(commands=['register'])
async def register_user(message: Message):
    logging_tg(message.chat.id, message)
    if not is_register(message):

        make_state(message.chat.id, "register")
        await bot.send_message(message.chat.id, "Введи cвоё имя, номер комнаты и пароль через пробел!😼")
    else:
        await bot.send_message(message.chat.id, "Вы уже зарегистрированы!😼")


@dispatcher.message_handler(commands=['food'])
async def food_hate(message: Message):
    logging_tg(message.chat.id, message)
    make_state(message.chat.id, "food")
    if is_register(message):
        await bot.send_message(message.chat.id,
                               "Расскажи, какие продукты ты не употребляешь, а какие блюда любишь, и мы учтём это при составлении меню 🥰")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['menu'])
async def menu(message: Message):
    logging_tg(message.chat.id, message)
    menu = session.query(Menu).all()
    if is_register(message):
        if len(menu) == 0:
            await bot.send_message(message.chat.id, "Меню пока что нет")
        else:
            await bot.send_message(message.chat.id, menu[0].menu_text)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['post_menu'])
async def menu(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        await bot.send_message(message.chat.id, messages['not_registered'])
    else:
        if not user[0].is_admin:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")
        else:
            make_state(message.chat.id, "post_menu")
            await bot.send_message(message.chat.id, "Введите сообщение с меню🍔")


@dispatcher.message_handler(commands=['time_to_pay'])
async def time_to_pay(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        await bot.send_message(message.chat.id, messages['not_registered'])
    else:
        if not user[0].is_admin:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")
        else:
            make_state(message.chat.id, "time_to_pay")
            await bot.send_message(message.chat.id,
                                   "Введите номер комнаты дату сумму платежа и если требуется имя например (203 11.02 50) в этом случае все живущие в 203 номере получат оповещение или (203 11.02 50 Саша) в этом случае оповещение получит только Саша из 203")


@dispatcher.message_handler(commands=['add_wish'])
async def want_to_add(message: Message):
    logging_tg(message.chat.id, message)
    if not is_register(message):
        await bot.send_message(message.chat.id, messages['not_registered'])
    else:
        await bot.send_message(message.chat.id, "Напишите свои пожелания нам!")
        make_state(message.chat.id, "want_to_add")


@dispatcher.message_handler(commands=['show_wishes'])
async def show_wish(message: Message):
    logging_tg(message.chat.id, message)
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) != 0:
        if user[0].is_admin == True:
            await bot.send_message(message.chat.id, await list_of_wish())
        else:
            await bot.send_message(message.chat.id, "Тебе сюда нелья!")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['what_close'])
async def what_close(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        await bot.send_message(message.chat.id, messages['what_close'])
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['events'])
async def events(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        await bot.send_message(message.chat.id, messages['events'])
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['show_feed_backs'])
async def show_feed_back(message: Message):
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if is_register(message):
        user = session.query(User).filter(User.telegram_id == message.chat.id).one()
        if user.is_admin:
            feed_backs = session.query(FeedBack).all()
            text_to_send = ""
            for i in feed_backs:
                user = session.query(User).filter(User.telegram_id == i.chat_id).one()
                text_to_send += f"{user.name} {user.room_number} фидбэк:{i.text}\n"
            await bot.send_message(message.chat.id, text_to_send)
        else:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя!")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['dogs'])
async def dogs(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        await bot.send_message(message.chat.id, messages['dogs'])
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['what_about_food'])
async def what_about_food(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        await bot.send_message(message.chat.id, messages['what_about_food'])
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['kitchen'])
async def kitchen(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        await bot.send_message(message.chat.id, "https://t.me/c/1638911958/27")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['cool_guys'])
async def services(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        await bot.send_message(message.chat.id, messages['price_of_all'])
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['show_who_eating'])
async def show_who_eating(message: Message):
    if is_register(message):
        user = session.query(User).filter(User.is_admin == True, User.telegram_id == message.chat.id).all()
        if len(user) == 0:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")
        else:
            logging_tg(message.chat.id, message)
            today = datetime.datetime.now().date()
            weekday = today.strftime("%A")
            rus_week_day = check_week_day(weekday)
            eat = session.query(Food).filter(Food.name_of_week_day == rus_week_day, Food.breakfast == True).all()
            message_to_send_breakfast = f"Кто ест сегодня завтрак :\n\n{len(eat)} порций\n\n"
            for i in eat:
                user = session.query(User).filter(User.id == i.user_id).one()
                if not user.food:
                    message_to_send_breakfast += f"{user.name} {user.room_number}\n"
                else:
                    message_to_send_breakfast += f"{user.name} {user.room_number} не ест {user.food}\n"

            eat_dinner = session.query(Food).filter(Food.name_of_week_day == rus_week_day, Food.dinner == True).all()
            message_to_send_dinner = f"\n\nКто ест сегодня обед : \n\n{len(eat_dinner)} порций\n\n"
            for i in eat_dinner:
                user = session.query(User).filter(User.id == i.user_id).one()
                if not user.food:
                    message_to_send_dinner += f"{user.name} {user.room_number}\n"
                else:
                    message_to_send_dinner += f"{user.name} {user.room_number} не ест {user.food}\n"
            message_to_send = message_to_send_breakfast + message_to_send_dinner
            await bot.send_message(message.chat.id, message_to_send)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['show_who_eating_for_week'])
async def show_who_eating_for_week(message: Message):
    if is_register(message):
        user = session.query(User).filter(User.is_admin == True, User.telegram_id == message.chat.id).all()
        if len(user) == 0:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя 🧐")
        else:
            await bot.send_message(message.chat.id, await show_who_eating_for_week_handler())
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler()
async def add_user(message: Message):
    user_state = session.query(State).filter(State.chat_id == message.chat.id).all()
    if user_state == 0:
        state = State(chat_id=message.chat.id, state="start")
        session.add(state)
        session.commit()
    else:
        if user_state[0].state == "get_feedback":
            await get_feed_back_handler(message, bot)
        if user_state[0].state == "meal":
            await when_to_eat_handler(message, bot)
        if user_state[0].state == "add_cleaning":
            await add_cleaning_handler(message, bot)
        if user_state[0].state == "added_cleaning":
            await change_text_cleaning_handler(message, bot)
        if user_state[0].state == "register":
            await register(message, bot)
        if user_state[0].state == "admin":
            await admin(message, bot)
        if user_state[0].state == "food":
            await food(message, bot)
        if user_state[0].state == "post_menu":
            await post_menu(message, bot)
        if user_state[0].state == "time_to_pay":
            await time_to_pay_handler(message, bot)
        if user_state[0].state == "wash_cloth":
            await wash_clothes_handler(message, bot)
        if user_state[0].state == "want_to_add":
            await want_to_add_wish(message, bot)
        if user_state[0].state == "delete_user":
            await delete_user_handler(message, bot)


executor.start_polling(dispatcher)
