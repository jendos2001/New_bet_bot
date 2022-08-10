import sqlite3
from copy import deepcopy
import os
import datetime
import src.config


class TennisDataBase:
    __database = None
    __instance = None
    __cursor = None

    def __init__(self, database_path):
        self.__database = sqlite3.connect(database_path)
        self.__cursor = self.__database.cursor()
        self.__make_db()

    def __make_db(self):
        self.__cursor.execute('CREATE TABLE IF NOT EXISTS tennis (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'user_id INTEGER, match_date TEXT, tournament INTEGER, round TEXT, '
                              'match_id INTEGER, team1 TEXT, team2 TEXT, bet TEXT, score TEXT, result TEXT)')
        self.__cursor.execute('CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'tournament TEXT, stage_id INTEGER, year)')

    def add_data(self, data):
        self.__cursor.execute("SELECT id FROM tournaments WHERE tournament = ?", (data['tournament'], ))
        if not self.__cursor.fetchall():
            self.__cursor.execute("INSERT INTO tournaments (tournament, stage_id, year)"
                                  "VALUES (?, ?, ?)", (data['tournament'], data['tournament_id'], data['year']))
        self.__cursor.execute("INSERT INTO tennis (user_id, match_date, tournament, round, match_id, team1, "
                              "team2, bet, result)"
                              "VALUES "
                              "(?, ?, (SELECT id FROM tournaments WHERE tournament = ?), ?, ?, ?, ?, ?, ?)",
                              (data['user_id'], data['match_date'], data['tournament'], data['round'],
                               data['match_id'], data['team1'], data['team2'], data['bet'], '*'))
        self.__database.commit()

    def tournaments(self, date, user_id):
        self.__cursor.execute(f"SELECT tournaments.tournament "
                              f"FROM tournaments INNER JOIN tennis ON tennis.tournament = tournaments.id "
                              f"WHERE tennis.match_date = ? AND tennis.user_id = ?"
                              f"GROUP BY 1",
                              (date, user_id))
        return self.__cursor.fetchall()

    def matches(self, date, user_id, tournament):
        self.__cursor.execute(f"SELECT team1, team2 "
                              f"FROM tennis "
                              f"WHERE match_date = ? AND "
                              f"tournament = (SELECT id FROM tournaments WHERE tournament = ?) "
                              f"AND user_id = ? AND result = '*'",
                              (date, tournament, user_id))
        return self.__cursor.fetchall()

    def match(self, date, user_id, team1, team2):
        self.__cursor.execute(f"SELECT bet "
                              f"FROM tennis "
                              f"WHERE match_date = ? AND user_id = ? AND team1 = ? AND team2 = ?",
                              (date, user_id, team1, team2))
        return self.__cursor.fetchall()

    def set_result(self, check_info):
        self.__cursor.execute(f"UPDATE tennis "
                              f"SET result = ? "
                              f"WHERE match_date = ? AND "
                              f"tournament = (SELECT id FROM tournaments WHERE tournament = ?) "
                              f"AND team1 = ? AND team2 = ?",
                              (check_info['result'], check_info['date'], check_info['tournament'], check_info['team1'],
                               check_info['team2']))
        self.__database.commit()

    def get_users(self):
        self.__cursor.execute(f"SELECT user_id "
                              f"FROM tennis "
                              f"GROUP BY 1")
        return self.__cursor.fetchall()

    def get_years(self):
        self.__cursor.execute(f"SELECT year "
                              f"FROM tournaments "
                              f"GROUP BY 1")
        return self.__cursor.fetchall()

    def get_tournaments_by_year(self, year):
        self.__cursor.execute(f"SELECT tournaments.tournament "
                              f"FROM tennis INNER JOIN tournaments ON tournaments.id = tennis.tournament "
                              f" WHERE tournaments.year = ?"
                              f"GROUP BY 1", (year, ))
        return self.__cursor.fetchall()

    def get_stats(self, stats_info):
        self.__cursor.execute(f"SELECT COUNT(*) "
                              f"FROM tennis INNER JOIN tournaments ON tournaments.id = tennis.tournament "
                              f"WHERE tournaments.year = ? AND tournaments.tournament = ? AND tennis.result = ?"
                              f"UNION ALL "
                              f"SELECT COUNT(*) "
                              f"FROM tennis INNER JOIN tournaments ON tournaments.id = tennis.tournament "
                              f"WHERE tournaments.year = ? AND tournaments.tournament = ? AND tennis.result = ?",
                              (stats_info['year'], stats_info['tournament'], '+',
                               stats_info['year'], stats_info['tournament'], '-'))
        return self.__cursor.fetchall()

    def set_autocheck(self, data, user_id):
        self.__cursor.execute(f"SELECT bet "
                              f"FROM tennis "
                              f"WHERE match_id = ? AND user_id = ?"
                              f"GROUP BY 1", (data['match_id'], user_id))
        tmp_winner = deepcopy(self.__cursor.fetchall())
        if len(tmp_winner) > 0:
            if tmp_winner[0][0] != data['winner']:
                result = '-'
            else:
                result = '+'
            self.__cursor.execute(f"UPDATE tennis "
                                  f"SET result = ?, score = ? "
                                  f"WHERE match_id = ? AND user_id = ?",
                                  (result, data['winner'], data['match_id'], user_id))
            self.__database.commit()

        self.__cursor.execute(f"SELECT team1, team2, bet, score, result "
                              f"FROM tennis "
                              f" WHERE tennis.match_id = ? AND user_id = ?"
                              f"GROUP BY 1", (data['match_id'], user_id))
        return self.__cursor.fetchall()

