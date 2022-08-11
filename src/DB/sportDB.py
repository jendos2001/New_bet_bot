from abc import ABC, abstractmethod


class SportDataBase(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def make_db(self):
        pass

    @abstractmethod
    def add_data(self, data):
        pass

    @abstractmethod
    def get_tournaments(self, date, user_id):
        pass

    @abstractmethod
    def get_matches(self, date, user_id, tournament):
        pass

    @abstractmethod
    def get_match(self, date, user_id, team1, team2):
        pass

    @abstractmethod
    def set_result(self, check_info):
        pass

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def get_years(self):
        pass

    @abstractmethod
    def get_tournaments_by_year(self, year):
        pass

    @abstractmethod
    def get_stats(self, stats_info):
        pass

    @abstractmethod
    def set_autocheck(self, data, user_id):
        pass
