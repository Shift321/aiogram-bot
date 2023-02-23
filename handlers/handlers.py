from datetime import datetime, date, timedelta

from database.db import session
from models.models import User, Menu, Washes, Wishes, Payments, Cleaning, Food, FeedBack
from utils.utils import make_state


async def register(message, bot):
    text = message.text.split()
    if len(text) != 3:
        await bot.send_message(message.chat.id, "Не правильный формат ввода")
    else:
        if text[2] != "ColibringLiver":
            await bot.send_message(message.chat.id, "Не правильный пароль")
        else:
            user = User(telegram_id=message.chat.id, name=text[0], room_number=text[1])
            session.add(user)
            session.commit()
            await bot.send_message(message.chat.id, f"Привет, {text[0]}, добро пожаловать!😁")
            make_state(message.chat.id, "start")


async def admin(message, bot):
    tg_id = message.chat.id
    user = session.query(User).filter(User.telegram_id == tg_id).one()
    if message.text == "CollibringCool":
        user.is_admin = True
        session.flush()
        session.commit()
        await bot.send_message(tg_id, "Теперь ты админ поздравляю не злоупотребляй властью🫡")
        make_state(message.chat.id, "start")
    else:
        await bot.send_message(message.chat.id, "Неправильный пароль попробуй еще раз")


async def food(message, bot):
    user = session.query(User).filter(User.telegram_id == message.chat.id).one()
    user.food = message.text
    session.flush()
    session.commit()
    await bot.send_message(message.chat.id, "Ваши предпочтения в еде записаны🍕")

    make_state(message.chat.id, "start")


async def post_menu(message, bot):
    menu = session.query(Menu).all()
    if len(menu) == 0:
        menu = Menu(menu_text=message.text)
        session.add(menu)
        session.commit()
    else:
        menu[0].menu_text = message.text
        session.flush()
        session.commit()

    make_state(message.chat.id, "start")
    await bot.send_message(message.chat.id, "Меню добавленно🥘")


async def time_to_pay_handler(message, bot):
    payers = message.text.split(" ")
    if len(payers) == 4:
        date_recieved = payers[1]
        date_of_pay = date_recieved + ".23"
        date_of_pay_obj = datetime.strptime(date_of_pay, '%d.%m.%y').date()
        users = session.query(User).filter(User.room_number == payers[0], User.name == payers[3]).all()
        sum_of_pay = payers[2]
        if len(users) == 0:
            await bot.send_message(message.chat.id, "Не найден ни один юзер что то введенно не так(")
        else:
            for user in users:
                payment = Payments(date_of_payment=date_of_pay_obj, user_id=user.id, sum_of_pay=sum_of_pay)
                session.add(payment)
                session.commit()
                session.flush()
            await bot.send_message(message.chat.id, "успех")
    else:
        date_recieved = payers[1]
        date_of_pay = date_recieved + ".23"
        date_of_pay_obj = datetime.strptime(date_of_pay, '%d.%m.%y').date()
        users = session.query(User).filter(User.room_number == payers[0]).all()
        sum_of_pay = payers[2]
        if len(users) == 0:
            await bot.send_message(message.chat.id, "Не найден ни один юзер что то введенно не так(")
        else:
            for user in users:
                payment = Payments(date_of_payment=date_of_pay_obj, user_id=user.id, sum_of_pay=sum_of_pay)
                session.add(payment)
                session.commit()
                session.flush()
            await bot.send_message(message.chat.id, "успех")


async def wash_clothes_handler(message, bot):
    time = message.text.split("-")
    format_ok = True
    try:
        time_start = datetime.strptime(time[0], '%H:%M').time()
        time_end = datetime.strptime(time[1], '%H:%M').time()
    except:
        format_ok = False
        await bot.send_message(message.chat.id, "Неправильный формат ввода")
    if format_ok:
        if time_start > time_end:
            await bot.send_message(message.chat.id, "Вы ввели неправильное время попробуйте еще раз")
        else:
            user = session.query(User).filter(User.telegram_id == message.chat.id).one()
            can_add_up = 0
            can_add_down = 0
            all_washes = session.query(Washes).all()
            if len(all_washes) == 0:
                wash = Washes(time_start=time_start, time_end=time_end, date=date.today(),
                              name=user.name)
                session.add(wash)
                session.commit()
                await bot.send_message(message.chat.id, "Готово")

                make_state(message.chat.id, "start")
            else:
                for wash in all_washes:
                    if time_start <= wash.time_start and time_start <= wash.time_end and time_end <= wash.time_start and time_end <= wash.time_end:
                        can_add_up += 1
                    if time_start >= wash.time_start and time_start >= wash.time_end and time_end >= wash.time_start and time_end >= wash.time_end:
                        can_add_down += 1
                result = can_add_up + can_add_down
                if can_add_up == len(all_washes) or can_add_down == len(all_washes) or result == len(all_washes):
                    wash = Washes(time_start=time_start, time_end=time_end, date=date.today(),
                                  name=user.name)
                    session.add(wash)
                    session.commit()
                    await bot.send_message(message.chat.id, "Готово")

                    make_state(message.chat.id, "start")
                else:
                    await bot.send_message(message.chat.id, "Данное время занято введите другое время")


async def want_to_add_wish(message, bot):
    user = session.query(User).filter(User.telegram_id == message.chat.id).one()
    wish = Wishes(name_of_user=user.name, text=message.text)
    session.add(wish)
    session.commit()
    await bot.send_message(message.chat.id, "Ваше пожелание записано!")

    make_state(message.chat.id, "start")


async def list_of_wish():
    wishes = session.query(Wishes).all()
    text = ""
    for wish in wishes:
        text += f"Имя :{wish.name_of_user}, Пожелание: {wish.text}" + "\n"
    return text


async def delete_user_handler(message, bot):
    text = message.text.split()
    user_to_delete = session.query(User).filter(User.name == text[0]).filter(User.room_number == text[1]).all()
    if len(user_to_delete) != 0:
        session.delete(user_to_delete[0])
        session.commit()
        await bot.send_message(message.chat.id, "Пользователь успешно удален")

        make_state(message.chat.id, "start")
    else:
        await bot.send_message(message.chat.id, "Такого пользователя нет")


async def add_cleaning_handler(message, bot):
    cleaning_days = message.text.split(",")
    for one_cleaning in cleaning_days:
        text = one_cleaning.split()
        week_day = text[0]
        room_number = text[1]
        new_cleaning = Cleaning(week_day=week_day, room_number=room_number)
        session.add(new_cleaning)
        session.commit()
    await bot.send_message(message.chat.id, "Готово")


async def when_to_eat_handler(message, bot):
    days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    meals = ['завтрак', 'обед']
    text = message.text.replace(":", "")
    when_to_eat = text.split(",")
    user = session.query(User).filter(User.telegram_id == message.chat.id).one()
    for i in when_to_eat:
        day = i.split()

        if day[0].lower() not in days:
            print(day[0].lower())
            print("wrong day")
            await bot.send_message(message.chat.id, f"Ошибка в слове {day[0].lower()}")
            return
        if len(day) == 3:
            if day[1] not in meals:
                print("wrong завтрак")
                await bot.send_message(message.chat.id, f"Ошибка в слове {day[1]}")
                return
            if day[2] not in meals:
                print("wrong обэд")
                await bot.send_message(message.chat.id, f"ошибка в слове {day[1]}")
                return
        if len(day) == 2:
            if day[1] not in meals:
                print("wrong завтрак или обэд")
                await bot.send_message(message.chat.id, "Вы ввели что то не так попробуйте еще раз")
                return
        lens = [3, 2]
        if len(day) not in lens:
            print("wrong len")
            await bot.send_message(message.chat.id, "Вы ввели что то не так попробуйте еще раз")
            return

    for day in when_to_eat:
        day = day.split()
        if len(day) == 3:
            check_eat = session.query(Food).filter(Food.user_id == user.id,
                                                   Food.name_of_week_day == day[0].lower()).all()
            if len(check_eat) != 0:
                check_eat[0].breakfast = True
                check_eat[0].dinner = True
                session.commit()
            else:
                eat = Food(name_of_week_day=day[0].lower(), user_id=user.id, breakfast=True,
                           dinner=True)
                session.add(eat)
                session.commit()
        else:
            if day[1].upper() == "ЗАВТРАК":
                check_eat = session.query(Food).filter(Food.user_id == user.id,
                                                       Food.name_of_week_day == day[0].lower()).all()
                if len(check_eat) != 0:
                    check_eat[0].breakfast = True
                    session.commit()
                else:
                    eat = Food(name_of_week_day=day[0].lower(), user_id=user.id, breakfast=True)
                    session.add(eat)
                    session.commit()
            if day[1].upper() == "ОБЕД":
                check_eat = session.query(Food).filter(Food.user_id == user.id,
                                                       Food.name_of_week_day == day[0].lower()).all()
                if len(check_eat) != 0:
                    check_eat[0].breakfast = True
                    session.commit()
                else:
                    eat = Food(name_of_week_day=day[0].lower(), user_id=user.id, dinner=True)
                    session.add(eat)
                    session.commit()
    await bot.send_message(message.chat.id, "Готово")


async def change_text_cleaning_handler(message, bot):
    now_day = date.today()
    tommorrow = now_day + timedelta(days=1)
    user = session.query(User).filter(User.telegram_id == message.chat.id).one()
    cleaning = session.query(Cleaning).filter(Cleaning.room_number == user.room_number,
                                              Cleaning.date == tommorrow).one()
    cleaning.text = message.text
    session.flush()
    session.commit()
    await bot.send_message(message.chat.id, "Готово Ваша просьба записана")


async def get_feed_back_handler(message, bot):
    text = message.text
    feed_back = FeedBack(chat_id=message.chat.id, text=text)
    session.add(feed_back)
    session.commit()
    await bot.send_message(message.chat.id, "Ваш фидбэк записан")
