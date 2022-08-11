import sqlite3
from copy import deepcopy
from src.DB.sportDB import SportDataBase


class TennisDataBase(SportDataBase):

    def __init__(self, database_path):
        self.__database = sqlite3.connect(database_path)
        self.__cursor = self.__database.cursor()
        self.make_db()

    def make_db(self):
        self.__cursor.execute('CREATE TABLE IF NOT EXISTS tennis (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'user_id INTEGER, match_date TEXT, tournament INTEGER, round TEXT, '
                              'match_id INTEGER, team1 INTEGER, team2 INTEGER, bet INTEGER, score INTEGER, '
                              'result TEXT)')
        self.__cursor.execute('CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'tournament TEXT, stage_id INTEGER, year)')
        self.__cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'user INTEGER)')
        self.__cursor.execute('CREATE TABLE IF NOT EXISTS sportsmans (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'sportsmen TEXT)')

    def add_data(self, data):
        self.__cursor.execute("SELECT id FROM tournaments WHERE tournament = ?", (data['tournament'],))
        if not self.__cursor.fetchall():
            self.__cursor.execute("INSERT INTO tournaments (tournament, stage_id, year)"
                                  "VALUES (?, ?, ?)", (data['tournament'], data['tournament_id'], data['year']))

        self.__cursor.execute("SELECT id FROM sportsmans WHERE sportsmen = ?", (data['team1'],))
        if not self.__cursor.fetchall():
            self.__cursor.execute("INSERT INTO sportsmans (sportsmen)"
                                  "VALUES (?)", (data['team1'],))

        self.__cursor.execute("SELECT id FROM sportsmans WHERE sportsmen = ?", (data['team2'],))
        if not self.__cursor.fetchall():
            self.__cursor.execute("INSERT INTO sportsmans (sportsmen)"
                                  "VALUES (?)", (data['team2'],))

        self.__cursor.execute("SELECT id FROM users WHERE user = ?", (data['user_id'],))
        if not self.__cursor.fetchall():
            self.__cursor.execute("INSERT INTO users (user)"
                                  "VALUES (?)", (data['user_id'],))

        self.__cursor.execute("INSERT INTO tennis (user_id, match_date, tournament, round, match_id, team1, "
                              "team2, bet, result)"
                              "VALUES "
                              "((SELECT id FROM users WHERE user = ?), ?, "
                              "(SELECT id FROM tournaments WHERE tournament = ?), ?, ?, "
                              "(SELECT id FROM sportsmans WHERE sportsmen = ?), "
                              "(SELECT id FROM sportsmans WHERE sportsmen = ?), "
                              "(SELECT id FROM sportsmans WHERE sportsmen = ?), ?)",
                              (data['user_id'], data['match_date'], data['tournament'], data['round'],
                               data['match_id'], data['team1'], data['team2'], data['bet'], '*'))
        self.__database.commit()

    def get_tournaments(self, date, user_id):
        self.__cursor.execute(f"SELECT tournaments.tournament "
                              f"FROM tournaments INNER JOIN tennis ON tennis.tournament = tournaments.id "
                              f"WHERE tennis.match_date = ? "
                              f"AND tennis.user_id = (SELECT id FROM users WHERE user = ?)"
                              f"GROUP BY 1",
                              (date, user_id))
        return self.__cursor.fetchall()

    def get_matches(self, date, user_id, tournament):
        self.__cursor.execute(f"SELECT team1, team2 "
                              f"FROM tennis INNER JOIN sportsmans ON tennis.team1 = sportsmans.id "
                              f"INNER JOIN sportsmans ON tennis.team2 = sportsmans.id "
                              f"WHERE match_date = ? AND "
                              f"tournament = (SELECT id FROM tournaments WHERE tournament = ?) "
                              f"AND user_id = (SELECT id FROM users WHERE user = ?) AND result = '*'",
                              (date, tournament, user_id))
        return self.__cursor.fetchall()

    def get_match(self, date, user_id, team1, team2):
        self.__cursor.execute(f"SELECT bet "
                              f"FROM tennis "
                              f"WHERE match_date = ? AND user_id = (SELECT id FROM users WHERE user = ?) "
                              f"AND team1 = (SELECT id FROM sportsmans WHERE sportsmen = ?) "
                              f"AND team2 = (SELECT id FROM sportsmans WHERE sportsmen = ?)",
                              (date, user_id, team1, team2))
        return self.__cursor.fetchall()

    def set_result(self, check_info):
        self.__cursor.execute(f"UPDATE tennis "
                              f"SET result = ? "
                              f"WHERE match_date = ? AND "
                              f"tournament = (SELECT id FROM tournaments WHERE tournament = ?) "
                              f"AND team1 = (SELECT id FROM sportsmans WHERE sportsmen = ?) "
                              f"AND team2 = (SELECT id FROM sportsmans WHERE sportsmen = ?)",
                              (check_info['result'], check_info['date'], check_info['tournament'],
                               check_info['team1'], check_info['team2']))
        self.__database.commit()

    def get_users(self):
        self.__cursor.execute(f"SELECT user "
                              f"FROM users "
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
                              f"GROUP BY 1", (year,))
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
                              f"WHERE match_id = ? AND user_id = (SELECT id FROM users WHERE user = ?) "
                              f"AND result = ? "
                              f"GROUP BY 1", (data['match_id'], user_id, '*'))
        tmp_winner = deepcopy(self.__cursor.fetchall())
        if len(tmp_winner) > 0:
            if tmp_winner[0][0] != data['winner']:
                result = '-'
            else:
                result = '+'
            self.__cursor.execute(f"UPDATE tennis "
                                  f"SET result = ?, score = ? "
                                  f"WHERE match_id = (SELECT id FROM sportsmans WHERE sportsmen = ?) "
                                  f"AND user_id = (SELECT id FROM users WHERE user = ?)",
                                  (result, data['winner'], data['match_id'], user_id))
            self.__database.commit()

        self.__cursor.execute(f"SELECT team1, team2, bet, score, result "
                              f"FROM tennis INNER JOIN sportsmans ON tennis.team1 = sportsmans.id "
                              f"INNER JOIN sportsmans ON tennis.team2 = sportsmans.id "
                              f"WHERE tennis.match_id = ? AND user_id = (SELECT id FROM users WHERE user = ?)"
                              f"GROUP BY 1", (data['match_id'], user_id))
        return self.__cursor.fetchall()
