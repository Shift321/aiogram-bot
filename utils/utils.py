import datetime

from database.db import session
from models.models import User, State, Food, Dinner
from utils.messages import choices


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


def first_course_help(poll_answer, user):
    all_user_food = session.query(Food).filter(Food.user_id == user.id, Food.dinner == True).all()
    for one_food in all_user_food:
        courses = session.query(Dinner).filter(Dinner.food_id == one_food.id, Dinner.first_course == True).all()
        for course in courses:
            course.first_course = False
            session.flush()
            session.commit()
        one_food.dinner = False
        session.flush()
        session.commit()

    for i in poll_answer.option_ids:
        try:
            foods_check_first = session.query(Food).filter(Food.name_of_week_day == choices[str(i)],
                                                           Food.user_id == user.id).all()
            if len(foods_check_first) == 0:
                foods_check_first = Food(name_of_week_day=choices[str(i)], user_id=user.id, dinner=True)
                session.add(foods_check_first)
                session.commit()
            else:
                foods_check_first[0].dinner = True
                session.flush()
                session.commit()
            food = session.query(Food).filter(Food.name_of_week_day == choices[str(i)],
                                              Food.user_id == user.id).one()
            check_dinners = session.query(Dinner).filter(Dinner.food_id == food.id).all()
            for dinner in check_dinners:
                dinner.first_course = False
                session.flush()
                session.commit()
            if len(check_dinners) == 0:
                dinner = Dinner(food_id=food.id, first_course=True)
                session.add(dinner)
                session.commit()
            else:
                check_dinners[0].first_course = True
                session.flush()
                session.commit()
        except KeyError:
            print("all good we keep going")
            pass


def second_course_help(poll_answer, user):
    all_user_food = session.query(Food).filter(Food.user_id == user.id, Food.dinner == True).all()
    for one_food in all_user_food:
        courses = session.query(Dinner).filter(Dinner.food_id == one_food.id, Dinner.second_course == True).all()
        for course in courses:
            course.second_course = False
            session.flush()
            session.commit()
        one_food.dinner = False
        session.flush()
        session.commit()

    for i in poll_answer.option_ids:
        try:
            foods_check_first = session.query(Food).filter(Food.name_of_week_day == choices[str(i)],
                                                           Food.user_id == user.id).all()
            if len(foods_check_first) == 0:
                foods_check_first = Food(name_of_week_day=choices[str(i)], user_id=user.id, dinner=True)
                session.add(foods_check_first)
                session.commit()
            else:
                foods_check_first[0].dinner = True
                session.flush()
                session.commit()
            food = session.query(Food).filter(Food.name_of_week_day == choices[str(i)],
                                              Food.user_id == user.id).one()
            check_dinners = session.query(Dinner).filter(Dinner.food_id == food.id).all()
            for dinner in check_dinners:
                dinner.second_course = False
                session.flush()
                session.commit()
            if len(check_dinners) == 0:
                dinner = Dinner(food_id=food.id, second_course=True)
                session.add(dinner)
                session.commit()
            else:
                check_dinners[0].second_course = True
                session.flush()
                session.commit()
        except KeyError:
            print("all good we keep going")
            pass


def breakfast_help(poll_answer, user):
    all_user_food = session.query(Food).filter(Food.user_id == user.id, Food.breakfast == True).all()
    for one_food in all_user_food:
        one_food.breakfast = False
        session.flush()
        session.commit()

    for i in poll_answer.option_ids:
        foods_check = session.query(Food).filter(Food.name_of_week_day == choices[str(i)],
                                                 Food.user_id == user.id).all()
        if len(foods_check) == 0:
            food_add = Food(name_of_week_day=choices[str(i)], user_id=user.id, breakfast=True)
            session.add(food_add)
            session.commit()
        else:
            foods_check[0].breakfast = True
            session.flush()
            session.commit()


def no_breakfast(user):
    all_food = session.query(Food).filter(Food.user_id == user.id).all()
    for food in all_food:
        food.breakfast = False
        session.flush()
        session.commit()


def no_first_course(user):
    all_food = session.query(Food).filter(Food.user_id == user.id, Food.dinner == True).all()
    for food in all_food:
        course = session.query(Dinner).filter(Dinner.food_id == food.id).one()
        course.first_course = False
        session.flush()
        session.commit()


def no_second_course(user):
    all_food = session.query(Food).filter(Food.user_id == user.id, Food.dinner == True).all()
    for food in all_food:
        course = session.query(Dinner).filter(Dinner.food_id == food.id).one()
        course.second_course = False
        session.flush()
        session.commit()


def what_to_eat_dinner(user, food):
    text = ''
    if food.breakfast:
        text = 'завтрак, '
    if food.dinner:
        course = session.query(Dinner).filter(Dinner.food_id == food.id).all()
        if len(course) == 0:
            pass
        else:
            if course[0].first_course:
                if course[0].second_course:
                    text += "суп и "
                else:
                    text += "суп"
            if course[0].second_course:
                text += "второе"
        return text
    else:
        return text



