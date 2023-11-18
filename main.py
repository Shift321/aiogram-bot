import json
from datetime import date
import datetime
from aiogram import Bot, executor, Dispatcher
from aiogram.types import Message, PollAnswer

from database.db import Base, engine, session
from handlers.handlers import register, admin, food, post_menu, time_to_pay_handler, wash_clothes_handler, \
    want_to_add_wish, list_of_wish, delete_user_handler, add_cleaning_handler, \
    change_text_cleaning_handler, get_feed_back_handler, show_who_eating_for_week_handler, birth_insert_handler, \
    change_room_handler, show_birth_handler, add_birthday_handler, show_user_food_handler, food_reminder_handler, \
    reserve_tv_handler, lection_reserve_handler

from models.models import User, Menu, Washes, Food, State, Cleaning, FeedBack, Dinner, Wishes, TvReserve, LectionReserve
from utils.messages import messages, command_list, admin_command_list, week_days, feed_back, payment_requisites
from utils.utils import logging_tg, is_register, check_week_day, make_state, first_course_help, breakfast_help, \
    second_course_help, no_breakfast, no_first_course, no_second_course

bot = Bot("5888170225:AAF49kmNi9IngDKghmYWUknvDhYZMYM3-Uc")
dispatcher = Dispatcher(bot)
Base.metadata.create_all(engine)


@dispatcher.message_handler(commands=['start'])
async def hello(message: Message):
    logging_tg(message.chat.id, message)
    make_state(message.chat.id, "start")
    await bot.send_message(message.chat.id, messages["hello_message_collibring"])
    await bot.send_message(message.chat.id, command_list)


@dispatcher.message_handler(commands=['show_user_food'])
async def show_user_food(message: Message):
    logging_tg(message.chat.id, message)
    make_state(message.chat.id, "show_user_food")
    await bot.send_message(message.chat.id, "Введите имя")


@dispatcher.message_handler(commands=['change_room'])
async def change_room(message: Message):
    if is_register(message):
        logging_tg(message.chat.id, message)
        make_state(message.chat.id, "change_room")
        await bot.send_message(message.chat.id, "Введите номер комнаты куда переехали")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['who_need_to_pay'])
async def who_need_to_pay(message: Message):
    if is_register(message):
        chat_id = message.chat.id
        user_admin = session.query(User).filter(User.telegram_id == chat_id).one()
        if user_admin.is_admin:
            text_to_send = 'Оплата за еду за эту неделю\n\n'
            food = session.query(Food).all()
            payments = {}
            for i in food:
                user = session.query(User).filter(User.id == i.user_id).one()
                if i.breakfast:
                    if user.id in payments.keys():
                        payments[user.id] += 10
                    else:
                        payments[user.id] = 10
                if i.dinner:
                    course = session.query(Dinner).filter(Dinner.food_id == i.id).one()
                    if course.first_course:
                        if user.id in payments.keys():
                            payments[user.id] += 10
                        else:
                            payments[user.id] = 10
                    if course.second_course:
                        if user.id in payments.keys():
                            payments[user.id] += 10
                        else:
                            payments[user.id] = 10
            for user_id in payments.keys():
                user = session.query(User).filter(User.id == user_id).one()
                text_to_send += f"{user.name} - {payments[user_id]} лари\n"
            await bot.send_message(message.chat.id, text_to_send)
        else:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['send_message_to_all'])
async def send_to_all(message: Message):
    if is_register(message):
        user = session.query(User).filter(User.telegram_id == message.chat.id).one()
        if user.is_admin:
            make_state(message.chat.id, "send_to_all")
            await bot.send_message(message.chat.id, "Введите текст чтобы отправить его всем")
        else:
            await bot.send_message(message.chat.id, "Тебе сюда нельзя уходи! ")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['meal'])
async def when_to_eat(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        poll = await message.answer_poll(question='Завтраки',
                                         allows_multiple_answers=True,
                                         options=week_days,
                                         is_anonymous=False)
        poll2 = await message.answer_poll(question='Обеды(первое)',
                                          allows_multiple_answers=True,
                                          options=week_days,
                                          is_anonymous=False)
        poll3 = await message.answer_poll(question='Обеды(второе)',
                                          allows_multiple_answers=True,
                                          options=week_days,
                                          is_anonymous=False)
        info_string = '{' + f'"tg_user_id": {message.from_user.id}, "breakfast": {poll.poll.id}, "first_course": {poll2.poll.id},"second_course": {poll3.poll.id}' + '}'
        user = session.query(User).filter(User.telegram_id == message.chat.id).one()
        user.info_string = info_string
        session.flush()
        session.commit()
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['pay'])
async def pay(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        make_state(message.chat.id, "pay")
        await bot.send_message(message.chat.id,
                               f"Оплату за жильё, питание, разбитую посуду и мероприятия можно перевести по счёту {payment_requisites}")
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
    now_day = datetime.date.today()
    weekday = now_day.strftime("%A")
    if is_register(message):
        cleanings = session.query(Cleaning).filter(Cleaning.week_day == check_week_day(weekday)).all()
        text_to_send = "Просьбы об уборке сегодня:\n\n"
        if len(cleanings) == 0:
            text_to_send = "На сегодня нет уборок"
        else:
            for cleaning in cleanings:
                if "," in str(cleaning.room_number):
                    for room_number in cleaning.room_number.split(","):
                        users = session.query(User).filter(User.room_number == room_number).all()
                        if len(users) == 0:
                            text_to_send += f"Комната: {room_number} в ней никто не живет\n"
                        for i in users:
                            if i.cleaning_prefers is not None:
                                text_to_send += f"Комната: {room_number} предпочтения:{i.cleaning_prefers}\n"
                                break
                            else:
                                text_to_send += f"Комната: {room_number} предпочтений нет\n"
                                break
                else:
                    room_number = cleaning.room_number
                    users = session.query(User).filter(User.room_number == room_number).all()
                    if len(users) == 0:
                        text_to_send += f"Комната: {room_number} в ней никто не живет"
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
        washes = session.query(Washes).filter(Washes.date >= date.today()).order_by(Washes.date, Washes.time_start)
        text = ""
        for wash in washes:
            time_start = str(wash.time_start)[:5]
            time_end = str(wash.time_end)[:5]
            text += f"{wash.name} {time_start}-{time_end} {wash.date}" + "\n\n"
        text += "Введите время желаемой стирки в формате 15:00-16:00-17.11.2023\n(если вы не укажите дату датой будет автоматически выбран сегодняшний день)"
        await bot.send_message(message.chat.id, text)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['reserve_tv'])
async def wash_clothes(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        make_state(message.chat.id, "reserve_tv")
        tv_reserves = session.query(TvReserve).filter(TvReserve.date >= date.today()).order_by(TvReserve.date,
                                                                                               TvReserve.time_start)
        text = ""
        for tv_reserve in tv_reserves:
            time_start = str(tv_reserve.time_start)[:5]
            time_end = str(tv_reserve.time_end)[:5]
            text += f"{tv_reserve.name} {time_start}-{time_end} {tv_reserve.date}" + "\n\n"
        text += "Введите время желаемой брони тв в формате 15:00-16:00-17.11.2023\n(если вы не укажите дату датой будет автоматически выбран сегодняшний день)"
        await bot.send_message(message.chat.id, text)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['lection_reserve'])
async def wash_clothes(message: Message):
    logging_tg(message.chat.id, message)
    if is_register(message):
        make_state(message.chat.id, "lection_reserve")
        lection_reserves = session.query(LectionReserve).filter(TvReserve.date >= date.today()).order_by(
            LectionReserve.date, LectionReserve.time_start)
        text = ""
        for lection_reserve in lection_reserves:
            time_start = str(lection_reserve.time_start)[:5]
            time_end = str(lection_reserve.time_end)[:5]
            text += f"{lection_reserve.name} {time_start}-{time_end} {lection_reserve.date}" + "\n\n"
        text += "Введите время желаемой брони лекционной в формате 15:00-16:00-17.11.2023\n(если вы не укажите дату датой будет автоматически выбран сегодняшний день)"
        await bot.send_message(message.chat.id, text)
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['clean_lections'])
async def clean_lections_and_tv(message: Message):
    all_lections = session.query(LectionReserve).all()
    for i in all_lections:
        session.delete(i)
        session.commit()
    all_tv = session.query(TvReserve).all()
    for i in all_tv:
        session.delete(i)
        session.commit()
    await bot.send_message(message.chat.id, "Готово")


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
        await bot.send_message(message.chat.id,
                               "Введи cвоё имя, номер комнаты, пароль и Дату рождения в формате (07.03.1999) через пробел!😼")
    else:
        await bot.send_message(message.chat.id, "Вы уже зарегистрированы!😼")


@dispatcher.message_handler(commands=['food'])
async def food_hate(message: Message):
    logging_tg(message.chat.id, message)
    make_state(message.chat.id, "food")
    if is_register(message):
        await bot.send_message(message.chat.id,
                               feed_back)
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


@dispatcher.message_handler(commands=['show_feed_backs'])
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


@dispatcher.message_handler(commands=['delete_all_food_and_send_message'])
async def do_shit(message: Message):
    all_food = session.query(Food).all()
    for i in all_food:
        course = session.query(Dinner).filter(Dinner.food_id == i.id).all()
        for j in course:
            session.delete(j)
            session.commit()
        session.delete(i)
        session.commit()
    users = session.query(User).all()
    for user in users:
        await bot.send_message(user.telegram_id,
                               "Привет! Перезапишись пожалуйста на еду !/meal")
    await bot.send_message(message.chat.id, "готово")


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
            message_to_send_breakfast = f"Кто ест сегодня завтрак: \n\n{len(eat)} порций\n\n"
            for i in eat:
                try:
                    user = session.query(User).filter(User.id == i.user_id).one()
                    if not user.food:
                        message_to_send_breakfast += f"{user.name} {user.room_number}\n"
                    else:
                        if len(user.food) > 3:
                            message_to_send_breakfast += f"{user.name} {user.room_number}\n"
                        else:
                            message_to_send_breakfast += f"{user.name} {user.room_number}\n"
                except:
                    session.delete(i)
                    session.commit()
            counter_first_course = 0
            counter_second_course = 0
            eat_dinner = session.query(Food).filter(Food.name_of_week_day == rus_week_day, Food.dinner == True).all()
            for one_dinner in eat_dinner:
                course = session.query(Dinner).filter(Dinner.food_id == one_dinner.id).all()
                if len(course) == 0:
                    pass
                else:
                    if course[0].first_course:
                        counter_first_course += 1
                    if course[0].second_course:
                        counter_second_course += 1
            message_to_send_dinner = f"\n\nКто ест сегодня обед : \n\nПервое: {counter_first_course} порций\nВторое: {counter_second_course} порций\n\n"
            for i in eat_dinner:
                user = session.query(User).filter(User.id == i.user_id).one()
                course = session.query(Dinner).filter(Dinner.food_id == i.id).all()
                if not user.food:
                    if course[0].first_course:
                        message_to_send_dinner += f"\n{user.name} {user.room_number} суп"
                        if course[0].second_course:
                            message_to_send_dinner += " и второе"
                    if course[0].second_course and course[0].first_course == False:
                        message_to_send_dinner += f"\n{user.name} {user.room_number} второе"
                else:
                    if len(user.food) > 3:
                        if course[0].first_course:
                            message_to_send_dinner += f"\n{user.name} {user.room_number} - суп"
                            if course[0].second_course:
                                message_to_send_dinner += " и второе"
                        if course[0].second_course and course[0].first_course == False:
                            message_to_send_dinner += f"\n{user.name} {user.room_number} второе"
                    else:
                        if course[0].first_course:
                            message_to_send_dinner += f"\n{user.name} {user.room_number} суп"
                            if course[0].second_course:
                                message_to_send_dinner += " и второе"
                        if course[0].second_course and course[0].first_course == False:
                            message_to_send_dinner += f"\n{user.name} {user.room_number} второе"
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


@dispatcher.message_handler(commands=['show_birth'])
async def show_birth(message: Message):
    if is_register(message):
        await bot.send_message(message.chat.id, show_birth_handler())
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['add_birthday'])
async def add_birthday(message: Message):
    if is_register(message):
        await bot.send_message(message.chat.id, "Введите дату своего рождения в формате 07.03.1999")
        make_state(message.chat.id, "add_birthday")
    else:
        await bot.send_message(message.chat.id, messages['not_registered'])


@dispatcher.message_handler(commands=['send_payment_info'])
async def send_payment_info(message: Message):
    for name in names.keys():
        user1 = session.query(User).filter(User.name == name).all()
        await bot.send_message(user1[0].telegram_id, f"Время платить за еду ! с тебя {names[name]} лари\n" + feed_back)
        make_state(user1[0].telegram_id, "get_feedback")
    await bot.send_message(message.chat.id, "ГОТОВО")

@dispatcher.message_handler(commands=['show_lera_food'])
async def show_lera_food(message:Message):
    lera = session.query(User).filter(User.name == "Валерия").one()
    food_of_lera = session.query(Food).filter(Food.user_id == lera.id).all()
    text_message = ""
    for i in food_of_lera:
        text_message += i.name_of_week_day
        text_message += i.breakfast
        text_message += i.dinner
        text_message += "\n\n"
    await bot.send_message(message.chat.id,text_message)

@dispatcher.message_handler(commands=['watch_prefers'])
async def send_prefers(message: Message):
    users = session.query(User).all()
    message_for_send = "Список пожеланий по еде :\n"
    for user in users:
        if not user.food:
            pass
        else:
            message_for_send += f"{user.name} из {user.room_number}. Предпочтения :{user.food}\n\n"
    await bot.send_message(message.chat.id, message_for_send)


@dispatcher.poll_answer_handler()
async def poll_answer(poll_answer: PollAnswer):
    users = session.query(User).all()
    for user in users:
        if user.info_string is not None:
            info_string = json.loads(user.info_string)
            if info_string['tg_user_id'] == poll_answer.user.id:
                information = json.loads(user.info_string)
                user_id = user.id
    user = session.query(User).filter(User.id == user_id).one()

    if information['breakfast'] == int(poll_answer.poll_id):
        if poll_answer.option_ids == [7]:
            no_breakfast(user)
        else:
            breakfast_help(poll_answer, user)

    if information['first_course'] == int(poll_answer.poll_id):
        if poll_answer.option_ids == [7]:
            no_first_course(user)
        else:
            first_course_help(poll_answer, user)

    if information['second_course'] == int(poll_answer.poll_id):
        if poll_answer.option_ids == [7]:
            no_second_course(user)
        else:
            second_course_help(poll_answer, user)
    foods = session.query(Food).filter(Food.user_id == user.id).all()
    for i in foods:
        courses = session.query(Dinner).filter(Dinner.food_id == i.id).all()
        if len(courses) == 0:
            pass
        else:
            if courses[0].first_course == False and courses[0].second_course == False:
                i.dinner = False
                session.flush()
                session.commit()
            else:
                i.dinner = True
                session.flush()
                session.commit()


@dispatcher.message_handler()
async def add_user(message: Message):
    user_state = session.query(State).filter(State.chat_id == message.chat.id).all()
    if user_state == 0:
        state = State(chat_id=message.chat.id, state="start")
        session.add(state)
        session.commit()
    else:
        if user_state[0].state == "add_birthday":
            await add_birthday_handler(message, bot)
        if user_state[0].state == "change_room":
            await change_room_handler(message, bot)
        if user_state[0].state == "send_to_all":
            await birth_insert_handler(message, bot)
        if user_state[0].state == "get_feedback":
            await get_feed_back_handler(message, bot)
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
        if user_state[0].state == "reserve_tv":
            await reserve_tv_handler(message, bot)
        if user_state[0].state == "lection_reserve":
            await lection_reserve_handler(message, bot)
        if user_state[0].state == "want_to_add":
            await want_to_add_wish(message, bot)
        if user_state[0].state == "delete_user":
            await delete_user_handler(message, bot)
        if user_state[0].state == "show_user_food":
            await show_user_food_handler(message, bot)
        if user_state[0].state == "food_reminder":
            await food_reminder_handler(message, bot)


executor.start_polling(dispatcher)
