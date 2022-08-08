import requests
import datetime
from copy import deepcopy
import src.Sports.sport_config


class Tennis:
    __tournaments = deepcopy(src.Sports.sport_config.tennis_tournaments)
    __tennis_matches = {}
    __users = {}
    __remaining_matches = None

    def __init__(self):
        self.__date = datetime.date.today()
        flashscore_url = "https://flashscore.p.rapidapi.com/v1/events/list"
        flashscore_querystring = {"indent_days": "0", "sport_id": "2", "timezone": "-8", "locale": "en_GB"}
        flashscore_headers = {
            "X-RapidAPI-Host": "flashscore.p.rapidapi.com",
            "X-RapidAPI-Key": src.Sports.sport_config.flashscore_key
        }

        self.__make_matches(requests.request("GET", flashscore_url,
                                             headers=flashscore_headers, params=flashscore_querystring).json()['DATA'])

    def __make_matches(self, tournaments):
        for item in tournaments:
            for elem in self.__tournaments.values():
                if item['TOURNAMENT_ID'] in elem.values():
                    matches = {}
                    for event in item['EVENTS']:
                        if event['STAGE'] != 'CANCELED' and event['STAGE'] != 'INTERRUPTED':
                            matches[event['SHORTNAME_AWAY'] + ' - ' + event['SHORTNAME_HOME']] = \
                                {'match_id': event['EVENT_ID'], 'teams': f"{event['HOME_NAME']} - {event['AWAY_NAME']}",
                                 'round': event['ROUND']}
                    self.__tennis_matches[item['NAME_PART_2']] = matches
                    self.__remaining_matches = deepcopy(self.__tennis_matches.copy())

    def add_user(self, user_id):
        self.__users[user_id] = deepcopy(self.__tennis_matches.copy())

    def get_date(self):
        return self.__date

    def get_matches(self, user_id):
        return self.__users[user_id]

    def delete_match(self, user_id, tournament, match):
        self.__users[user_id][tournament].pop(match)

    def get_users(self):
        return self.__users.keys()
