import datetime
from datetime import timedelta
import time

import requests

from database.db import session
from models.models import Payments, User, Cleaning, Food, Dinner
from utils.messages import cleaning_time, feed_back
from utils.utils import make_state, check_week_day

url = f"https://api.telegram.org/bot5888170225:AAEN6YCV3hBD6G54Kb9tHuDeRajpY_Uicug/sendMessage"


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
            for room_number in cleaning.room_number.split(","):
                print(room_number)
                users = session.query(User).filter(User.room_number == room_number).all()
                for user in users:
                    make_state(user.telegram_id, "added_cleaning")
                    send_message(user_id=user.telegram_id, text_to_send=cleaning_time)
                    if make_text_for_cleaning() is not None:
                        send_message(user_id=user.telegram_id, text_to_send=make_text_for_cleaning())
                    cleaning.sended = True
                    session.flush()
                    session.commit()


def send_paymet_food():
    users = session.query(User).filter(User.recieve_payment_message == False).all()
    food = session.query(Food).all()
    for user in users:
        summ_to_pay = 0
        for i in food:
            if i.user_id == user.id:
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

        print("here")
        if summ_to_pay == 0:
            return
        else:
            send_message(user_id=user.telegram_id,
                         text_to_send=f"Время платить за еду ! с тебя {summ_to_pay}\n" + feed_back)
            make_state(user.telegram_id, "get_feedback")
            user.recieve_payment_message = True
            session.flush()
            session.commit()


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
    session.delete(all_food)
    session.commit()


def check_time(hour, minute):
    now = datetime.datetime.now().time()
    if now.hour == hour and now.minute == minute:
        return True
    else:
        return False


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
        if check_time(11, 00):
            delete_food()
        if check_time(9, 00):
            send_paymet_food()
    if check_time(11, 00):
        check_payments()
    if check_time(12, 00):
        check_cleaning()
    time.sleep(5)
