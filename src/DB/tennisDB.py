from copy import deepcopy
from src.DB.sportDB import SportDataBase


class TennisDataBase(SportDataBase):

    def __init__(self, database_path):
        super().__init__(database_path)

    def _make_db(self):
        self._cursor.execute('CREATE TABLE IF NOT EXISTS tennis (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'user_id INTEGER REFERENCES users(id), match_date INTEGER REFERENCES dates(id), '
                             'tournament INTEGER REFERENCES tournaments(id), round INTEGER REFERENCES rounds (id), '
                             'match_id INTEGER, team1 INTEGER REFERENCES sportsman(id), '
                             'team2 INTEGER REFERENCES sportsman(id), bet INTEGER, score INTEGER, '
                             'result TEXT)')
        self._cursor.execute('CREATE TABLE IF NOT EXISTS tournaments (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'tournament TEXT, stage_id INTEGER, year)')
        self._cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'user INTEGER)')
        self._cursor.execute('CREATE TABLE IF NOT EXISTS sportsman (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'sportsmen TEXT)')
        self._cursor.execute('CREATE TABLE IF NOT EXISTS rounds (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'round TEXT)')
        self._cursor.execute('CREATE TABLE IF NOT EXISTS dates (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'date TEXT)')

    def add_data(self, data):
        self._cursor.execute("SELECT id FROM tournaments WHERE tournament = ? AND stage_id = ?",
                             (data['tournament'], data['tournament_id']))
        if not self._cursor.fetchall():
            self._cursor.execute("INSERT INTO tournaments (tournament, stage_id, year)"
                                 "VALUES (?, ?, ?)", (data['tournament'], data['tournament_id'], data['year']))

        self._cursor.execute("SELECT id FROM sportsman WHERE sportsmen = ?", (data['team1'],))
        if not self._cursor.fetchall():
            self._cursor.execute("INSERT INTO sportsman (sportsmen)"
                                 "VALUES (?)", (data['team1'],))

        self._cursor.execute("SELECT id FROM sportsman WHERE sportsmen = ?", (data['team2'],))
        if not self._cursor.fetchall():
            self._cursor.execute("INSERT INTO sportsman (sportsmen)"
                                 "VALUES (?)", (data['team2'],))

        self._cursor.execute("SELECT id FROM users WHERE user = ?", (data['user_id'],))
        if not self._cursor.fetchall():
            self._cursor.execute("INSERT INTO users (user)"
                                 "VALUES (?)", (data['user_id'],))

        self._cursor.execute("SELECT id FROM dates WHERE date = ?", (data['match_date'],))
        if not self._cursor.fetchall():
            self._cursor.execute("INSERT INTO dates (date)"
                                 "VALUES (?)", (data['match_date'],))

        self._cursor.execute("SELECT id FROM rounds WHERE round = ?", (data['round'],))
        if not self._cursor.fetchall():
            self._cursor.execute("INSERT INTO rounds (round)"
                                 "VALUES (?)", (data['round'],))

        self._cursor.execute("INSERT INTO tennis (user_id, match_date, tournament, round, match_id, team1, "
                             "team2, bet, result)"
                             "VALUES "
                             "((SELECT id FROM users WHERE user = ?), "
                             "(SELECT id FROM dates WHERE date = ?), "
                             "(SELECT id FROM tournaments WHERE tournament = ?), "
                             "(SELECT id FROM rounds WHERE round = ?), ?, "
                             "(SELECT id FROM sportsman WHERE sportsmen = ?), "
                             "(SELECT id FROM sportsman WHERE sportsmen = ?), "
                             "(SELECT id FROM sportsman WHERE sportsmen = ?), ?)",
                             (data['user_id'], data['match_date'], data['tournament'], data['round'],
                              data['match_id'], data['team1'], data['team2'], data['bet'], '*'))
        self._database.commit()

    def get_tournaments(self, date, user_id):
        self._cursor.execute(f"SELECT tournaments.tournament "
                             f"FROM tournaments INNER JOIN tennis ON tennis.tournament = tournaments.id "
                             f"WHERE tennis.match_date = (SELECT id FROM dates WHERE date = ?) "
                             f"AND tennis.user_id = (SELECT id FROM users WHERE user = ?)"
                             f"GROUP BY 1",
                             (date, user_id))
        return self._cursor.fetchall()

    def get_matches(self, date, user_id, tournament):
        self._cursor.execute(f"SELECT team1, team2 "
                             f"FROM tennis INNER JOIN sportsman ON tennis.team1 = sportsman.id "
                             f"INNER JOIN sportsman ON tennis.team2 = sportsman.id "
                             f"WHERE match_date = (SELECT id FROM dates WHERE date = ?) AND "
                             f"tournament = (SELECT id FROM tournaments WHERE tournament = ?) "
                             f"AND user_id = (SELECT id FROM users WHERE user = ?) AND result = '*'",
                             (date, tournament, user_id))
        return self._cursor.fetchall()

    def get_match(self, date, user_id, team1, team2):
        self._cursor.execute(f"SELECT bet "
                             f"FROM tennis "
                             f"WHERE match_date = (SELECT id FROM dates WHERE date = ?) "
                             f"AND user_id = (SELECT id FROM users WHERE user = ?) "
                             f"AND team1 = (SELECT id FROM sportsman WHERE sportsmen = ?) "
                             f"AND team2 = (SELECT id FROM sportsman WHERE sportsmen = ?)",
                             (date, user_id, team1, team2))
        return self._cursor.fetchall()

    def set_result(self, check_info):
        self._cursor.execute(f"UPDATE tennis "
                             f"SET result = ? "
                             f"WHERE match_date = (SELECT id FROM dates WHERE date = ?) AND "
                             f"tournament = (SELECT id FROM tournaments WHERE tournament = ?) "
                             f"AND team1 = (SELECT id FROM sportsman WHERE sportsmen = ?) "
                             f"AND team2 = (SELECT id FROM sportsman WHERE sportsmen = ?)",
                             (check_info['result'], check_info['date'], check_info['tournament'],
                              check_info['team1'], check_info['team2']))
        self._database.commit()

    def get_users(self):
        self._cursor.execute(f"SELECT user "
                             f"FROM users "
                             f"GROUP BY 1")
        return self._cursor.fetchall()

    def get_years(self):
        self._cursor.execute(f"SELECT year "
                             f"FROM tournaments "
                             f"GROUP BY 1")
        return self._cursor.fetchall()

    def get_tournaments_by_year(self, year):
        self._cursor.execute(f"SELECT tournaments.tournament "
                             f"FROM tennis INNER JOIN tournaments ON tournaments.id = tennis.tournament "
                             f" WHERE tournaments.year = ?"
                             f"GROUP BY 1", (year,))
        return self._cursor.fetchall()

    def get_stats(self, stats_info):
        self._cursor.execute(f"SELECT COUNT(*) "
                             f"FROM tennis INNER JOIN tournaments ON tournaments.id = tennis.tournament "
                             f"WHERE tournaments.year = ? AND tournaments.tournament = ? AND tennis.result = ?"
                             f"UNION ALL "
                             f"SELECT COUNT(*) "
                             f"FROM tennis INNER JOIN tournaments ON tournaments.id = tennis.tournament "
                             f"WHERE tournaments.year = ? AND tournaments.tournament = ? AND tennis.result = ?",
                             (stats_info['year'], stats_info['tournament'], '+',
                              stats_info['year'], stats_info['tournament'], '-'))
        return self._cursor.fetchall()

    def set_autocheck(self, data, user_id):
        self._cursor.execute(f"SELECT sportsman.sportsmen "
                             f"FROM tennis INNER JOIN sportsman ON tennis.bet = sportsman.id "
                             f"WHERE match_id = ? AND user_id = (SELECT id FROM users WHERE user = ?) "
                             f"AND result = ? "
                             f"GROUP BY 1", (data['match_id'], user_id, '*'))
        tmp_winner = deepcopy(self._cursor.fetchall())
        if len(tmp_winner) > 0:
            if tmp_winner[0][0] != data['winner']:
                result = '-'
            else:
                result = '+'
            self._cursor.execute(f"UPDATE tennis "
                                 f"SET result = ?, score = (SELECT id FROM sportsman WHERE sportsmen = ?) "
                                 f"WHERE match_id = ? "
                                 f"AND user_id = (SELECT id FROM users WHERE user = ?)",
                                 (result, data['winner'], data['match_id'], user_id))
            self._database.commit()

        self._cursor.execute(f"SELECT s1.sportsmen, s2.sportsmen, s3.sportsmen, s4.sportsmen, result "
                             f"FROM tennis INNER JOIN sportsman AS s1 ON tennis.team1 = s1.id "
                             f"INNER JOIN sportsman AS s2 ON tennis.team2 = s2.id "
                             f"INNER JOIN sportsman AS s3 ON tennis.bet = s3.id "
                             f"INNER JOIN sportsman AS s4 ON tennis.score = s4.id "
                             f"WHERE tennis.match_id = ? AND user_id = (SELECT id FROM users WHERE user = ?)"
                             f"GROUP BY 1", (data['match_id'], user_id))
        return self._cursor.fetchall()
