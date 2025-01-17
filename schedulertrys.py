import schedule
import time as tm
from datetime import time, timedelta, datetime

def job():
    print("my name is skyler yoo")

schedule.every().second.do(job)

while True:
    schedule.run_pending()
    tm.sleep(1)

