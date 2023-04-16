from sqlalchemy import MetaData, Date, Integer, String
from migrate.versioning.schema import Table, Column

from database.db import engine, session
from models.models import User


def send_not():
    users = session.query(User).filter(User.recieve_payment_message == True).all()
    for user in users:
        user.recieve_payment_message = False
        session.flush()
        session.commit()