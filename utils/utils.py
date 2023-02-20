import datetime

from database.db import session
from models.models import User, State


def logging_tg(tg_id, message):
    user = session.query(User).filter(User.telegram_id == tg_id).all()
    if len(user) == 0:
        print(
            f"{datetime.datetime.now()} User name: \"unregistered\" User tg id: {message.chat.id}. Message:{message.text}")
    else:
        print(
            f"{datetime.datetime.now()} User name: \"{user[0].name}\" User tg id: \"{message.chat.id}\" Message:\"{message.text}\"")


def is_register(message):
    user = session.query(User).filter(User.telegram_id == message.chat.id).all()
    if len(user) == 0:
        return False
    else:
        return True


def check_week_day(week_day):
    rus_week_day = ""
    if week_day == "Monday":
        rus_week_day = "понедельник"
    if week_day == "Tuesday":
        rus_week_day = "вторник"
    if week_day == "Wednesday":
        rus_week_day = "среда"
    if week_day == "Thursday":
        rus_week_day = "четверг"
    if week_day == "Friday":
        rus_week_day = "пятница"
    if week_day == "Saturday":
        rus_week_day = "суббота"
    if week_day == "Sunday":
        rus_week_day = "воскресенье"

    return rus_week_day


def make_state(chat_id, state_name):
    state = session.query(State).filter(State.chat_id == chat_id).all()
    if len(state) != 0:
        state[0].state = state_name
        session.flush()
        session.commit()
    else:
        state = State(chat_id=chat_id, state=state_name)
        session.add(state)
        session.commit()
