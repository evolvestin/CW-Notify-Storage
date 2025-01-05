import re

GAME_BASE_YEAR = 1061  # Reference game year
GAME_BASE_TIMESTAMP = 1532034000  # Unix timestamp for the reference date (31 Hailag 1060 00:00)
SECONDS_IN_A_DAY = 24 * 60 * 60  # Number of seconds in a day

# Time offset for different servers
GAME_SERVER_TIME_OFFSET = {'cw2': 0, 'cw2ru': 0, 'local': 0, 'cw3': 60 * 60}

# Number of days from the beginning of the game year for each month
GAME_MONTH_DAYS = {
    'Wintar': 0,
    'Hornung': 31,
    'Lenzin': 59,
    'Ōstar': 90,
    'Winni': 120,
    'Brāh': 151,
    'Hewi': 181,
    'Aran': 212,
    'Witu': 243,
    'Wīndume': 273,
    'Herbist': 304,
    'Hailag': 334,
}


def convert_game_date_to_timestamp(game_date: str, server_type: str) -> int:
    """
    Converts a game date to a Unix timestamp, considering the specifics of the game calendar.

    :param game_date: Date in the game format 'DD Month YYYY HH:MM', e.g., '31 Hailag 1061 12:30'
    :type game_date: str

    :param server_type: Server name, such as 'cw2', 'cw2ru', 'cw3', affecting the time offset
    :type server_type: str

    :return: Unix timestamp adjusted for the game time and server offset.
        Returns 0 if the date does not match the expected format.
    :rtype: int
    """
    search = re.search(r'(\d{2}) (.*?) (\d{4}) (\d{2}):(\d{2})', game_date)
    if search:
        day, month, year, hour, minute = search.groups()
        day, year, hour, minute = map(int, [day, year, hour, minute])

        years_after_base = (year - GAME_BASE_YEAR)  # Number of years since the reference year
        days_in_year = years_after_base * 365  # Total days since the reference year

        # Account for leap years (post-start)
        if years_after_base > 0:
            days_in_year += years_after_base // 4
            if year % 4 == 0 and month not in ['Wintar', 'Hornung']:
                days_in_year += 1

        total_seconds = (
            days_in_year * SECONDS_IN_A_DAY
            + GAME_MONTH_DAYS[month] * SECONDS_IN_A_DAY
            + day * SECONDS_IN_A_DAY
            + hour * 60 * 60
            + minute * 60
        )
        return GAME_BASE_TIMESTAMP + int(total_seconds / 3) + GAME_SERVER_TIME_OFFSET.get(server_type, 0)
    return 0
