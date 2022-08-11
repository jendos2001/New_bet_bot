import requests
import datetime
from copy import deepcopy
import src.Sports.sport_config


class Sport:

    def __init__(self, sport_id):
        self._date = (datetime.datetime.now() - datetime.timedelta(hours=8)).date()
        flashscore_url = "https://flashscore.p.rapidapi.com/v1/events/list"
        flashscore_querystring = {"indent_days": "0", "sport_id": sport_id, "timezone": "-8", "locale": "en_GB"}
        flashscore_headers = {
            "X-RapidAPI-Host": "flashscore.p.rapidapi.com",
            "X-RapidAPI-Key": src.Sports.sport_config.flashscore_key
        }
        self._tournaments = deepcopy(src.Sports.sport_config.tennis_tournaments)
        self._tennis_matches = {}
        self._check_id = {}
        self._users = {}
        self._make_matches(requests.request("GET", flashscore_url,
                                            headers=flashscore_headers, params=flashscore_querystring).json()['DATA'])

    def _make_matches(self, tournaments):
        pass

    def add_user(self, user_id):
        self._users[user_id] = deepcopy(self._tennis_matches.copy())

    def get_date(self):
        return self._date

    def get_matches(self, user_id):
        return self._users[user_id]

    def get_id(self):
        return self._check_id

    def delete_match(self, user_id, tournament, match):
        self._users[user_id][tournament].pop(match)

    def get_users(self):
        return self._users.keys()
