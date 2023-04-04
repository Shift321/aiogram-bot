from datetime import datetime, date, timedelta

from database.db import session
from models.models import User, Menu, Washes, Wishes, Payments, Cleaning, Food, FeedBack, Dinner
from utils.utils import make_state, check_week_day, what_to_eat_dinner


async def register(message, bot):
    text = message.text.split()
    if len(text) != 4:
        await bot.send_message(message.chat.id, "Не правильный формат ввода")
    else:
        if text[2] != "ColibringLiver":
            await bot.send_message(message.chat.id, "Не правильный пароль")
        else:
            user = User(telegram_id=message.chat.id, name=text[0], room_number=text[1],
                        birth=datetime.strptime(text[3], "%d.%m.%Y").date())
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
    users = session.query(User).all()
    for user in users:
        await bot.send_message(user.telegram_id, "Меню обновлено, запишись на питание!")
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
            all_washes = session.query(Washes).filter(Washes.date == date.today()).all()
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
    # понедельник 203,204,205; вторник 101,102,103;
    cleaning_days = message.text.split(";")
    for one_cleaning in cleaning_days:
        text = one_cleaning.split()
        week_day = text[0]
        room_number = text[1]
        cleaning = session.query(Cleaning).filter(Cleaning.week_day == week_day.lower()).all()
        if len(cleaning) == 0:
            new_cleaning = Cleaning(week_day=week_day.lower(), room_number=room_number)
            session.add(new_cleaning)
            session.commit()
        else:
            cleaning[0].room_number = room_number
            session.flush()
            session.commit()
    await bot.send_message(message.chat.id, "Готово")


async def change_text_cleaning_handler(message, bot):
    user = session.query(User).filter(User.telegram_id == message.chat.id).one()
    user.cleaning_prefers = message.text
    session.flush()
    session.commit()
    await bot.send_message(message.chat.id, "Готово Ваша просьба записана")


async def get_feed_back_handler(message, bot):
    text = message.text
    feed_back = FeedBack(chat_id=message.chat.id, text=text)
    session.add(feed_back)
    session.commit()
    await bot.send_message(message.chat.id, "Ваш фидбэк записан")


async def show_who_eating_for_week_handler():
    text_to_send = "Питающиеся на неделю:\n\n"
    monday_breakfast_counter = 0
    monday_first_course_counter = 0
    monday_second_course_counter = 0
    monday_text = f"Понедельник:\n\n"
    tuesday_breakfast_counter = 0
    tuesday_first_course_counter = 0
    tuesday_second_course_counter = 0
    tueday_text = f"Вторник:\n\n"
    wednsedey_breakfast_counter = 0
    wednsedey_first_course_counter = 0
    wednsedey_second_course_counter = 0
    wednsedey_text = f"Среда:\n\n"
    thurdsday_breakfast_counter = 0
    thurdsday_first_course_counter = 0
    thurdsday_second_course_counter = 0
    thurdsday_text = f"Четверг:\n\n"
    friday_breakfast_counter = 0
    friday_first_course_counter = 0
    friday_second_course_counter = 0
    friday_text = f"Пятница:\n\n"
    saturday_breakfast_counter = 0
    saturday_first_course_counter = 0
    saturday_second_course_counter = 0
    saturday_text = f"Суббота:\n\n"
    sunday_breakfast_counter = 0
    sunday_first_course_counter = 0
    sunday_second_course_counter = 0
    sunday_text = f"Воскресенье:\n\n"
    all_food = session.query(Food).all()
    for i in all_food:
        user = session.query(User).filter(User.id == i.user_id).all()
        if len(user) == 0:
            session.delete(i)
            session.commit()
        else:
            course = session.query(Dinner).filter(Dinner.food_id == i.id).all()
            if len(course) == 0:
                course = Dinner(food_id=i.id)
                session.add(course)
                session.commit()
            if i.name_of_week_day == "понедельник":
                if i.breakfast:
                    monday_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        monday_first_course_counter += 1
                    if course[0].second_course:
                        monday_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                monday_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
            if i.name_of_week_day == "вторник":
                if i.breakfast:
                    tuesday_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        tuesday_first_course_counter += 1
                    if course[0].second_course:
                        tuesday_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                tueday_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
            if i.name_of_week_day == "среда":
                if i.breakfast:
                    wednsedey_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        wednsedey_first_course_counter += 1
                    if course[0].second_course:
                        wednsedey_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                wednsedey_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
            if i.name_of_week_day == "четверг":
                if i.breakfast:
                    thurdsday_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        thurdsday_first_course_counter += 1
                    if course[0].second_course:
                        thurdsday_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                thurdsday_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
            if i.name_of_week_day == "пятница":
                if i.breakfast:
                    friday_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        friday_first_course_counter += 1
                    if course[0].second_course:
                        friday_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                friday_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
            if i.name_of_week_day == "суббота":
                if i.breakfast:
                    saturday_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        saturday_first_course_counter += 1
                    if course[0].second_course:
                        saturday_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                saturday_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
            if i.name_of_week_day == "воскресенье":
                if i.breakfast:
                    sunday_breakfast_counter += 1
                if i.dinner:
                    if course[0].first_course:
                        sunday_first_course_counter += 1
                    if course[0].second_course:
                        sunday_second_course_counter += 1
                user = session.query(User).filter(User.id == i.user_id).one()
                sunday_text += f"Имя: {user.name} - {what_to_eat_dinner(user, food=i)}\n"
    monday_counter = f"\n\nКоличество завтраков: {monday_breakfast_counter}\nКоличество обедов - первое: {monday_first_course_counter}, второе:{monday_second_course_counter}\n\n"
    tueday_counter = f"\n\nКоличество завтраков: {tuesday_breakfast_counter}\nКоличество обедов - первое: {tuesday_first_course_counter}, второе:{tuesday_second_course_counter}\n\n"
    wednsedey_counter = f"\n\nКоличество завтраков: {wednsedey_breakfast_counter}\nКоличество обедов - первое: {wednsedey_first_course_counter}, второе:{wednsedey_second_course_counter}\n\n"
    thurdsday_counter = f"\n\nКоличество завтраков: {thurdsday_breakfast_counter}\nКоличество обедов - первое: {thurdsday_first_course_counter}, второе:{thurdsday_second_course_counter}\n\n"
    friday_counter = f"\n\nКоличество завтраков: {friday_breakfast_counter}\nКоличество обедов - первое: {friday_first_course_counter}, второе:{friday_second_course_counter}\n\n"
    saturday_counter = f"\n\nКоличество завтраков: {saturday_breakfast_counter}\nКоличество обедов - первое: {saturday_first_course_counter}, второе:{saturday_second_course_counter}\n\n"
    sunday_counter = f"\n\nКоличество завтраков:{sunday_breakfast_counter}\nКоличество обедов - первое: {sunday_first_course_counter}, второе:{sunday_second_course_counter}\n\n"
    text_to_send += monday_text + monday_counter + "\n" + tueday_text + tueday_counter + "\n" + wednsedey_text + wednsedey_counter + "\n" + thurdsday_text + thurdsday_counter + "\n" + friday_text + friday_counter + "\n" + saturday_text + saturday_counter + "\n" + sunday_text + sunday_counter

    return text_to_send


async def birth_insert_handler(message, bot):
    users = session.query(User).all()
    for user in users:
        await bot.send_message(user.telegram_id, message.text)
    await bot.send_message(message.chat.id, "Готово")


async def change_room_handler(message, bot):
    user = session.query(User).filter(User.telegram_id == message.chat.id).one()
    if message.text.isdigit():
        user.room_number = int(message.text)
        session.flush()
        session.commit()
        await bot.send_message(message.chat.id, "Готово")
        make_state(message.chat.id, "start")
    else:
        await bot.send_message(message.chat.id, "вы ввели не число попробуйте еще раз")


def show_birth_handler():
    now = datetime.now().date()

    # Get all the users from the database
    users = session.query(User).all()

    # Calculate the number of days until each user's birthday
    days_until_birthdays = {}
    for user in users:
        if user.birth is not None:
            birthday = user.birth.replace(year=now.year)
            if birthday < now:
                birthday = birthday.replace(year=now.year + 1)
            days_until_birthdays[user] = (birthday - now).days
        else:
            pass
    # Sort the users based on the number of days until their birthday
    users = sorted(days_until_birthdays.keys(), key=lambda user: days_until_birthdays[user])
    message = 'Ближайшие дни рождения:\n\n'
    for user in users:
        if days_until_birthdays[user] == 0:
            message += f"У {user.name} из {user.room_number} cегодня день рождения!!\n"
        elif days_until_birthdays[user] == 1:
            message += f"У {user.name} из {user.room_number} завтра день рождения!!\n"
        else:
            message += f"У {user.name} из {user.room_number} день рождения через {days_until_birthdays[user]}\n"
    return message
