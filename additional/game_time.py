import os
from datetime import datetime
game_month = {'Wintar': 1, 'Hornung': 2, 'Lenzin': 3, 'Ōstar': 4, 'Winni': 5, 'Brāh': 6,
              'Hewi': 7, 'Aran': 8, 'Witu': 9, 'Wīndume': 10, 'Herbist': 11, 'Hailag': 12}
server_name = os.environ['server']
server = {'cw2': 1, 'cw3': 2}


def timer(search):
    stamp = int(datetime.now().timestamp())
    bissextile = [64, 68, 72, 76, 80]
    s_minute = int(search.group(5))
    s_hour = int(search.group(4))
    s_year = int(search.group(3))
    s_month = str(search.group(2))
    s_day = int(search.group(1))
    day = 24 * 60 * 60
    day31 = 31 * day
    day30 = 30 * day
    day28 = 28 * day
    seconds = -day
    sec = ((stamp + server[server_name] * 60 * 60 - 1530309600) * 3)
    seconds += day30 + day31 + 31536000 * (s_year - 61)  # Game standard
    month = game_month[s_month]

    if s_year in bissextile:
        day28 += day

    for i in bissextile:
        if s_year > i:
            seconds += day

    if month == 2:
        seconds += day31
    elif month == 3:
        seconds += day31 + day28
    elif month == 4:
        seconds += day31 + day28 + day31
    elif month == 5:
        seconds += day31 + day28 + day31 + day30
    elif month == 6:
        seconds += day31 + day28 + day31 + day30 + day31
    elif month == 7:
        seconds += day31 + day28 + day31 + day30 + day31 + day30
    elif month == 8:
        seconds += day31 + day28 + day31 + day30 + day31 + day30 + day31
    elif month == 9:
        seconds += day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31
    elif month == 10:
        seconds += day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30
    elif month == 11:
        seconds += day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31
        if s_year == 60:
            seconds = -day
    elif month == 12:
        seconds += day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31 + day30
        if s_year == 60:
            seconds = day30 - day

    seconds += s_day * day
    seconds += s_hour * 60 * 60
    seconds += s_minute * 60
    stack = int(stamp + (seconds - sec) / 3)
    return stack
