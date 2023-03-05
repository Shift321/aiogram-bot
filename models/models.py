from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey
from database.db import Base


class User(Base):
    __tablename__ = "client"

    id: int = Column(Integer, primary_key=True, index=True)
    telegram_id: int = Column(Integer)
    name: int = Column(Integer)
    room_number: int = Column(Integer)
    food: str = Column(String)
    is_admin: bool = Column(Boolean, default=False)
    days_of_meal: str = Column(String)
    recieve_payment_message: bool = Column(Boolean, default=False)
    cleaning_prefers: str = Column(String)


class Menu(Base):
    __tablename__ = "menu"

    id: int = Column(Integer, primary_key=True, index=True)
    menu_text: str = Column(String)


class Washes(Base):
    __tablename__ = "washes"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String)
    time_start: datetime = Column(Time)
    time_end: datetime = Column(Time)
    date = Column(Date)


class Wishes(Base):
    __tablename__ = "wishes"

    id: int = Column(Integer, primary_key=True, index=True)
    name_of_user: str = Column(String)
    text: str = Column(String)


class Payments(Base):
    __tablename__ = "payments"

    id: int = Column(Integer, primary_key=True, index=True)
    date_of_payment: date = Column(Date)
    user_id: int = Column(Integer, ForeignKey('client.id'))
    sum_of_pay: int = Column(Integer)


class Cleaning(Base):
    __tablename__ = "cleaning"

    id: int = Column(Integer, primary_key=True, index=True)
    date: date = Column(Date)
    text: str = Column(String)
    room_number: int = Column(Integer)
    sended: bool = Column(Boolean, default=False)
    week_day: str = Column(String)


class Food(Base):
    __tablename__ = "food"

    id: int = Column(Integer, primary_key=True, index=True)
    name_of_week_day: str = Column(String)
    user_id: int = Column(Integer, ForeignKey('client.id'))
    breakfast: bool = Column(Boolean, default=False)
    dinner: bool = Column(Boolean, default=False)


class State(Base):
    __tablename__ = "state"

    id: int = Column(Integer, primary_key=True, index=True)
    chat_id: int = Column(Integer)
    state: str = Column(String)


class FeedBack(Base):
    __tablename__ = "feed_back"

    id: int = Column(Integer, primary_key=True, index=True)
    chat_id: int = Column(Integer)
    text: str = Column(String)
