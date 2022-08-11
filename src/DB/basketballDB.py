from src.DB.sportDB import SportDataBase


class BasketballDataBase(SportDataBase):

    def __init__(self, database_path):
        super().__init__(database_path)

    def make_db(self):
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
