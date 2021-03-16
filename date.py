import datetime

CLOSING_US = '11:00PM'
deltas = {
    'closing price t': 1,
    'closing price t+1': 2,
    'closing price t+7': 7,
}

# adjust closed days for the respective year
nyse_closed= ['2021-01-01', '2021-01-18', '2021-02-15', '2021-04-02', '2021-05-31', '2021-07-05', '2021-09-06', '2021-12-24']
CLOSED = [(datetime.datetime.strptime(date, '%Y-%m-%d').date() + datetime.timedelta(days=0)) for date in nyse_closed]

def yesterday():
    today = datetime.date.today()
    day = datetime.date.today().day
    if day == 7:
        yesterday = today - datetime.timedelta(days=2)
    elif day == 1:
        yesterday = today - datetime.timedelta(days=3)
    else:
        yesterday = today - datetime.timedelta(days=1)
    return yesterday


def time_delta_sufficient(logdate, delta):
    today = datetime.date.today()
    t0 = datetime.datetime.strptime(logdate, '%Y-%m-%d').date()
    time_delta = (today - t0).days

    def market_closed(date):
        if date.weekday() == 5 or date.weekday() == 6:
            date = date + datetime.timedelta(days=2)
        if date in CLOSED:
            date = date + datetime.timedelta(days=1)
        return date

    # scraped the same day and markets not yet closed
    if time_delta == delta and datetime.datetime.now().time() < datetime.datetime.strptime(CLOSING_US,'%I:%M%p').time():
        return False, 0
    # scraped on saturday and it is at least Tuesday > t0 is Monday
    elif t0.weekday() == 5 and today.weekday() > 0:
        date_to_quote = t0 + datetime.timedelta(days=delta + 2)
        date_to_quote = market_closed(date_to_quote)
        if date_to_quote < today:
            return True, date_to_quote
        else:
            return False, 0
    # scraped on sunday and it is at least Tuesday > t0 is Monday
    elif t0.weekday() == 6 and today.weekday() > 0:
        date_to_quote = t0 + datetime.timedelta(days=delta + 1)
        date_to_quote = market_closed(date_to_quote)
        if date_to_quote < today:
            return True, date_to_quote
        else:
            return False, 0
    elif time_delta >= delta:
        date_to_quote = t0 + datetime.timedelta(days=delta)
        date_to_quote = market_closed(date_to_quote)
        if date_to_quote < today:
            return True, date_to_quote
        else:
            return False, 0
    elif time_delta < delta:
        return False, 0
