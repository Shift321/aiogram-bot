import datetime
from datetime import timedelta
import time

import requests

from database.db import session
from models.models import Payments, User, Cleaning, Food, Dinner
from utils.messages import cleaning_time, payment_requisites
from utils.utils import make_state, check_week_day

url = f"https://api.telegram.org/bot6565624535:AAHcgTNJT9IwEIW6eeaf67PvD_JwpVEVRao/sendMessage"


def check_payments():
    payments = session.query(Payments).filter(Payments.date_of_payment == datetime.date.today()).all()
    if len(payments) == 0:
        return
    else:
        for payment in payments:
            user = session.query(User).filter(User.id == payment.user_id).one()
            send_message(user.telegram_id, f"Привет! Пришло время оплатить жильё: {payment.sum_of_pay}")
            session.delete(payment)
            session.flush()
            session.commit()


def make_text_for_cleaning():
    now_day = datetime.date.today()
    tommorrow = now_day + timedelta(days=1)
    text_to_send = "Кстати вот , что уже занято. Пожалуйста отталкиваясь от этого напишите ваши предпочтения\n\n"
    cleanings = session.query(Cleaning).filter(Cleaning.date == tommorrow, Cleaning.text != None).all()
    if len(cleanings) == 0:
        return None
    else:
        for i in cleanings:
            text_to_send += f"Номер комнаты: {i.room_number} Просьба:{i.text}\n\n"
        return text_to_send


def check_cleaning():
    now_day = datetime.date.today()
    yestarday = now_day + timedelta(days=1)
    weekday = yestarday.strftime("%A")
    cleanings = session.query(Cleaning).filter(Cleaning.week_day == check_week_day(weekday),
                                               Cleaning.sended == False).all()
    if len(cleanings) == 0:
        return
    else:
        for cleaning in cleanings:
            if "," in str(cleaning.room_number):
                for room_number in cleaning.room_number.split(","):
                    users_cleaning_rooms = session.query(User).filter(User.room_number == room_number).all()
                    if len(users_cleaning_rooms) == 0:
                        pass
                    else:
                        for i in users_cleaning_rooms:
                            make_state(i.telegram_id, "added_cleaning")
                            send_message(user_id=i.telegram_id, text_to_send=cleaning_time)
                            text_for_cleaning = make_text_for_cleaning()
                            if text_for_cleaning is not None:
                                send_message(user_id=i.telegram_id, text_to_send=text_for_cleaning)
                            cleaning.sended = True
                            session.flush()
                            session.commit()
            else:
                room_number = cleaning.room_number
                users_cleaning_one_room = session.query(User).filter(User.room_number == room_number).all()
                if len(users_cleaning_one_room) == 0:
                    pass
                else:
                    for j in users_cleaning_one_room:
                        make_state(j.telegram_id, "added_cleaning")
                        send_message(user_id=j.telegram_id, text_to_send=cleaning_time)
                        if make_text_for_cleaning() is not None:
                            send_message(user_id=j.telegram_id, text_to_send=make_text_for_cleaning())
                        cleaning.sended = True
                        session.flush()
                        session.commit()


def send_payment_food():
    users_food = session.query(User).filter(User.recieve_payment_message == False).all()
    food = session.query(Food).all()
    for user_food in users_food:
        print(f"senging to {user_food.name} {user_food.room_number}")
        summ_to_pay = 0
        for i in food:
            if i.user_id == user_food.id:
                if i.breakfast:
                    summ_to_pay += 10
                if i.dinner:
                    course = session.query(Dinner).filter(Dinner.food_id == i.id).all()
                    if len(course) == 0:
                        pass
                    else:
                        if course[0].first_course:
                            summ_to_pay += 10
                        if course[0].second_course:
                            summ_to_pay += 10
        if summ_to_pay == 0:
            pass
        else:
            send_message(user_id=user_food.telegram_id,
                         text_to_send=f"Время платить за еду ! с тебя {summ_to_pay}\n\n Реквизиты для оплаты: {payment_requisites}\n")
            user_food.recieve_payment_message = True
            session.flush()
            session.commit()


def send_food_reminder():
    users = session.query(User).all()
    for user in users:
        send_message(user_id=user.telegram_id,
                     text_to_send="Напиши пожелания по меню на следующую неделю: какие блюда понравились, а какие больше не готовить, что нового хотелось бы попробовать?")
        make_state(chat_id=user.telegram_id, state_name='food_reminder')


def send_message(user_id, text_to_send):
    data = {
        "chat_id": user_id,
        "text": text_to_send
    }
    response = requests.post(url, json=data)


def make_sended_false():
    cleanings = session.query(Cleaning).all()
    for i in cleanings:
        i.sended = False
        session.flush()
        session.commit()


def delete_food():
    all_food = session.query(Food).all()
    for i in all_food:
        course = session.query(Dinner).filter(Dinner.food_id == i.id).all()
        for j in course:
            session.delete(j)
            session.commit()
        session.delete(i)
        session.commit()


def check_time(hour, minute):
    now = datetime.datetime.now().time()
    if now.hour == hour and now.minute == minute:
        return True
    else:
        return False


def delete_cleaning():
    users = session.query(User).all()
    for user in users:
        user.cleaning_prefers = ""
        session.flush()
        session.commit()


friday_sended = False
while True:
    today = datetime.datetime.now().date()
    weekday = today.strftime("%A")
    done_this_week = False
    if weekday == "Monday" and done_this_week == False:
        make_sended_false()
        done_this_week = True
    once = True
    tumbler = False
    if weekday == "Tuesday":
        done_this_week = True
        once = True
    if weekday == "Monday" and once:
        once = False
        tumbler = True
    if tumbler:
        users = session.query(User).all()
        for user in users:
            user.recieve_payment_message = False
        tumbler = False
    if weekday == "Sunday":
        if check_time(13, 00):
            delete_cleaning()
            delete_food()
        if check_time(12, 36):
            send_payment_food()
    if check_time(11, 00):
        check_payments()
    if check_time(12, 00):
        check_cleaning()
    if weekday == "Saturday":
        friday_sended = False
    if weekday == "Friday" and friday_sended == False:
        if check_time(10, 18):
            send_food_reminder()
        friday_sended = True

    time.sleep(5)
