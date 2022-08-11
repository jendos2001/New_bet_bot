import sqlite3


class SportDataBase:

    def __init__(self, database_path):
        self._database = sqlite3.connect(database_path)
        self._cursor = self._database.cursor()
        self._make_db()

    def _make_db(self):
        pass

    def add_data(self, data):
        pass

    def get_tournaments(self, date, user_id):
        pass

    def get_matches(self, date, user_id, tournament):
        pass

    def get_match(self, date, user_id, team1, team2):
        pass

    def set_result(self, check_info):
        pass

    def get_users(self):
        pass

    def get_years(self):
        pass

    def get_tournaments_by_year(self, year):
        pass

    def get_stats(self, stats_info):
        pass

    def set_autocheck(self, data, user_id):
        pass
