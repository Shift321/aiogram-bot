import datetime
from datetime import timedelta
today = datetime.datetime.now().date() + timedelta(days=6)
weekday = today.strftime("%A")
print(weekday)


