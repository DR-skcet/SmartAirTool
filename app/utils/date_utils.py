from datetime import date, timedelta

def generate_dates(months: int):
    dates = []
    today = date.today()
    for i in range(0, months * 4):  # every week
        day = today + timedelta(days=i * 7)
        dates.append(day.isoformat())
    return dates