from datetime import datetime
import pytz

def is_nse_market_open():

    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    if now.weekday() >= 5:  # Sat/Sun
        return False

    open_time = now.replace(hour=9, minute=15, second=0)
    close_time = now.replace(hour=15, minute=30, second=0)

    return open_time <= now <= close_time