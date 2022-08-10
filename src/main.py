from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config
import datetime
import requests
import Sports.Tennis
from DB.tennisDB import TennisDataBase


class MainClass:
    tennis_DB = None

    def __init__(self):
        self.match_info = {}
        self.check_info = {}
        self.stats_info = {}
        self.tennis_data = Sports.Tennis.Tennis()
        self.updater = Updater(token=config.token, use_context=True)

    @staticmethod
    def start(update, context):
        buttons = [[InlineKeyboardButton(text='Баскетбол', callback_data='basketball'),
                   InlineKeyboardButton(text='Теннис', callback_data='tennis'),
                   InlineKeyboardButton(text='Футбол', callback_data='football')]]
        menu = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери вид спорта', reply_markup=menu)

    def check_bet(self, update, context):
        data = update.callback_query.data
        if len(self.match_info) == 5 and self.match_info['kind_of_sport'] == 'tennis':
            self.match_info['bet'] = data
            s = "Проверь ставку:\nТеннис: {}\nСтавка: {}".format(self.tennis_data.get_matches(
                update.effective_chat.id)[self.match_info['tournament']][self.match_info['match']]['teams'],
                                                                 self.match_info['bet'])
            buttons = [[InlineKeyboardButton(text='Да, всё верно', callback_data='tennis_add_match')],
                       [InlineKeyboardButton(text='Нет, вернуться к матчам', callback_data='back_tennis_matches')],
                       [InlineKeyboardButton(text='Нет, вернуться к турнирам',
                                             callback_data='back_tennis_tournaments')]]
            tennis_confirm = InlineKeyboardMarkup(buttons)
            context.bot.send_message(chat_id=update.effective_chat.id, text=s, reply_markup=tennis_confirm)

    def answers(self, update, context):
        print(self.match_info)
        self.check_bet(update, context)
        data = update.callback_query.data
        if data == 'basketball':
            self.basketball(update, context)
        elif data == 'tennis':
            self.tennis(update, context)
        elif data == 'football':
            self.football(update, context)
        elif data == 'basketball_check':
            self.basketball_check(update, context)
        elif data == 'tennis_check':
            self.tennis_check(update, context)
        elif data == 'back_tournament_check':
            self.check_info.clear()
            self.check_info['sport'] = 'tennis'
            self.tennis_check(update, context)
        elif len(data.split(' - ')) == 2 and data.split(' - ')[1] == 'check':
            self.tournament_check(update, context)
        elif len(data.split(' - ')) == 3 and self.check_info['sport'] == 'tennis':
            self.check_tennis_match(update, context)
        elif data == '+' or data == '-':
            self.set_tennis_bet(update, context)
        elif data == 'football_check':
            self.football_check(update, context)
        elif data == 'back_check':
            self.check_info.clear()
            self.check(update, context)
        elif data == 'back_stats':
            self.stats_info.clear()
            self.stats(update, context)
        elif data == 'basketball_stats':
            self.basketball_stats(update, context)
        elif data == 'tennis_stats':
            self.tennis_stats(update, context)
        elif data.split(' - ')[0].isnumeric() and data.split(' - ')[1] == 'tennis_stats':
            self.tennis_tournaments(update, context)
        elif len(data.split(' - ')) == 2 and data.split(' - ')[1] == 'tennis_stats':
            self.get_stats(update, context)
        elif data == 'football_stats':
            self.football_stats(update, context)
        elif data in self.tennis_data.get_matches(update.effective_chat.id).keys():
            self.tennis_matches(update, context)
        elif data in self.tennis_data.get_matches(update.effective_chat.id)[self.match_info['tournament']].keys():
            self.tennis_match(update, context)
        elif data == 'back':
            self.match_info.clear()
            self.start(update, context)
        elif data == 'back_tennis_tournaments':
            self.match_info.clear()
            self.match_info['kind_of_sport'] = 'tennis'
            self.match_info['user'] = update.effective_chat.id
            self.tennis(update, context)
        elif data == 'back_tennis_matches':
            tmp_tornament = self.match_info['tournament']
            tmp_sport = self.match_info['kind_of_sport']
            self.match_info.clear()
            self.match_info['tournament'] = tmp_tornament
            self.match_info['kind_of_sport'] = tmp_sport
            self.match_info['user'] = update.effective_chat.id
            self.tennis_matches(update, context, tmp_tornament)
        elif data == 'tennis_add_match':
            self.tennis_add_match(update, context)

    def basketball(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='basketball')

    def tennis(self, update, context):
        self.match_info['kind_of_sport'] = 'tennis'
        self.match_info['user'] = update.effective_chat.id
        print(self.tennis_data.get_date())
        if (datetime.datetime.now() - datetime.timedelta(hours=8)).date() != self.tennis_data.get_date():
            print(1)
            self.tennis_data = Sports.Tennis.Tennis()
        if update.effective_chat.id not in self.tennis_data.get_users():
            print(2)
            self.tennis_data.add_user(update.effective_chat.id)
        print(self.tennis_data.get_date())
        buttons = []
        for key in self.tennis_data.get_matches(update.effective_chat.id).keys():
            buttons.append([InlineKeyboardButton(text=key, callback_data=key)])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спорта', callback_data='back')])
        tennis_tournaments = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери турнир', reply_markup=tennis_tournaments)

    def tennis_matches(self, update, context, tmp_tournament=None):
        if tmp_tournament is None:
            data = update.callback_query.data
        else:
            data = tmp_tournament
        self.match_info['tournament'] = data
        self.match_info['tournament_id'] = self.tennis_data.get_id()[data]
        print(self.match_info['tournament_id'])
        buttons = []
        for key, value in self.tennis_data.get_matches(update.effective_chat.id)[data].items():
            text = f"{value['teams']} - {value['round']}"
            buttons.append([InlineKeyboardButton(text=text, callback_data=key)])
        buttons.append([InlineKeyboardButton(text='Вернуться к турнирам', callback_data='tennis')])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спорта', callback_data='back')])
        matches = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери матч', reply_markup=matches)

    def tennis_match(self, update, context):
        data = update.callback_query.data
        self.match_info['match'] = data
        match = self.tennis_data.get_matches(update.effective_chat.id)[
            self.match_info['tournament']][data]['teams'].split(' - ')
        buttons = [[InlineKeyboardButton(text=match[0], callback_data=match[0])],
                   [InlineKeyboardButton(text=match[1], callback_data=match[1])]]
        current_match = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери победителя', reply_markup=current_match)

    def tennis_add_match(self, update, context):
        data = {'user_id': self.match_info['user'], 'match_date': str(datetime.date.today()),
                'tournament': self.match_info['tournament'],
                'round': self.tennis_data.get_matches(update.effective_chat.id)[
                    self.match_info['tournament']][self.match_info['match']]['round'],
                'year': datetime.datetime.now().year,
                'match_id': self.tennis_data.get_matches(update.effective_chat.id)[
                    self.match_info['tournament']][self.match_info['match']]['match_id'],
                'team1': self.tennis_data.get_matches(update.effective_chat.id)[
                    self.match_info['tournament']][self.match_info['match']]['teams'].split(' - ')[0],
                'team2': self.tennis_data.get_matches(update.effective_chat.id)[
                    self.match_info['tournament']][self.match_info['match']]['teams'].split(' - ')[1],
                'bet': self.match_info['bet'], 'tournament_id': self.match_info['tournament_id']}
        self.tennis_data.delete_match(update.effective_chat.id, self.match_info['tournament'], self.match_info['match'])
        self.tennis_DB = TennisDataBase(config.tennis_DB)
        self.tennis_DB.add_data(data)
        buttons = [[InlineKeyboardButton(text='Продолжить', callback_data='back_tennis_matches')]]
        continue_add = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Матч добавлен', reply_markup=continue_add)

    @staticmethod
    def check(update, context):
        buttons = [[InlineKeyboardButton(text='Баскетбол', callback_data='basketball_check'),
                    InlineKeyboardButton(text='Теннис', callback_data='tennis_check'),
                    InlineKeyboardButton(text='Футбол', callback_data='football_check')]]
        menu = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери вид спорта для проверки',
                                 reply_markup=menu)

    def tennis_check(self, update, context):
        self.check_info['sport'] = 'tennis'
        self.tennis_DB = TennisDataBase(config.tennis_DB)
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        print(date)
        self.check_info['date'] = date
        buttons = []
        for elem in self.tennis_DB.tournaments(date, update.effective_chat.id):
            text = f"{elem[0]} - check"
            buttons.append([InlineKeyboardButton(text=elem[0], callback_data=text)])
        buttons.append([InlineKeyboardButton(text='Вернуться в начало проверки', callback_data='back_check')])
        tournaments = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери турнир для проверки',
                                 reply_markup=tournaments)

    def tournament_check(self, update, context):
        data = update.callback_query.data
        self.check_info['tournament'] = data.split(' - ')[0]
        db = TennisDataBase(config.tennis_DB)
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        buttons = []
        for elem in self.tennis_DB.matches(date, update.effective_chat.id, data.split(' - ')[0]):
            text = f"{elem[0]} - {elem[1]}"
            data = f"{elem[0]} - {elem[1]} - check"
            buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
        buttons.append([InlineKeyboardButton(text='Вернуться к турнирам для проверки',
                                             callback_data='back_tournament_check')])
        buttons.append([InlineKeyboardButton(text='Вернуться в начало проверки', callback_data='back_check')])
        matches = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери матч для проверки',
                                 reply_markup=matches)

    def check_tennis_match(self, update, context):
        data = update.callback_query.data
        self.check_info['team1'] = data.split(' - ')[0]
        self.check_info['team2'] = data.split(' - ')[1]
        db = TennisDataBase(config.tennis_DB)
        date = datetime.date.today() - datetime.timedelta(days=1)
        buttons = [[InlineKeyboardButton(text='+', callback_data='+')],
                   [InlineKeyboardButton(text='-', callback_data='-')]]
        check_menu = InlineKeyboardMarkup(buttons)
        info = db.match(date, update.effective_chat.id, self.check_info['team1'], self.check_info['team2'])
        s = f"Матч: {data.split(' - ')[0]} - {data.split(' - ')[1]}\nСтавка: {info[0][0]}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=s,
                                 reply_markup=check_menu)

    def set_tennis_bet(self, update, context):
        data = update.callback_query.data
        self.check_info['result'] = data
        db = TennisDataBase(config.tennis_DB)
        db.set_result(self.check_info)
        check_continue_button = InlineKeyboardButton(text='Продолжить', callback_data='back_check')
        check_continue = InlineKeyboardMarkup([[check_continue_button]])
        context.bot.send_message(chat_id=update.effective_chat.id, text='Результат добален!',
                                 reply_markup=check_continue)

    def football(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='football')

    @staticmethod
    def stats(update, context):
        buttons = [[InlineKeyboardButton(text='Баскетбол', callback_data='basketball_stats'),
                    InlineKeyboardButton(text='Теннис', callback_data='tennis_stats'),
                    InlineKeyboardButton(text='Футбол', callback_data='football_stats')]]
        menu = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери вид спорта для получения статистики',
                                 reply_markup=menu)

    def tennis_stats(self, update, context):
        self.stats_info['sport'] = 'tennis'
        db = TennisDataBase(config.tennis_DB)
        buttons = []
        for elem in db.get_years():
            text = str(elem[0])
            data = f"{elem[0]} - tennis_stats"
            buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спортам со статистикой',
                                             callback_data='back_stats')])
        years = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери год',
                                 reply_markup=years)

    def tennis_tournaments(self, update, context):
        self.stats_info['year'] = int(update.callback_query.data.split(' - ')[0])
        db = TennisDataBase(config.tennis_DB)
        buttons = []
        for elem in db.get_tournaments_by_year(self.stats_info['year']):
            text = str(elem[0])
            data = f"{elem[0]} - tennis_stats"
            buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спортам со статистикой',
                                             callback_data='back_stats')])
        years = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери год',
                                 reply_markup=years)

    def get_stats(self, update, context):
        self.stats_info['tournament'] = update.callback_query.data.split(' - ')[0]
        db = TennisDataBase(config.tennis_DB)
        buttons = []
        results = db.get_stats(self.stats_info)
        print(results)
        plus = u'\U00002705'
        minus = u'\U0000274C'
        s = f"{self.stats_info['tournament']} - {self.stats_info['year']}\n{plus}{results[0][0]}" \
            f"\n{minus}{results[1][0]}"
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спортам со статистикой',
                                             callback_data='back_stats')])
        stats = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text=s,
                                 reply_markup=stats)

    @staticmethod
    def message(context):
        db = TennisDataBase(config.tennis_DB)
        for elem in db.get_users():
            context.bot.send_message(chat_id=elem[0], text='Не пора ли проставить матчи?')

    def autocheck(self, context):
        db = TennisDataBase(config.tennis_DB)
        for key, value in self.tennis_data.get_id().items():
            url = "https://flashscore.p.rapidapi.com/v1/tournaments/results"
            querystring = {"locale": "en_GB", "tournament_stage_id": value, "page": "1"}
            headers = {
                "X-RapidAPI-Key": "97e3e90f2dmsh490b0ed8c6df919p1c5460jsn31ae902c52e8",
                "X-RapidAPI-Host": "flashscore.p.rapidapi.com"
            }
            response = requests.request("GET", url, headers=headers, params=querystring).json()['DATA'][0]['EVENTS']
            for user_id in db.get_users():
                for elem in response:
                    data = {'match_id': elem['EVENT_ID']}
                    if elem['WINNER'] == 1:
                        data['winner'] = elem['HOME_NAME']
                    else:
                        data['winner'] = elem['AWAY_NAME']
                    tmp = db.set_autocheck(data, user_id[0])
                    if len(tmp) > 0:
                        s = f"Результат проставлен\nМатч: {tmp[0][0]} - {tmp[0][1]}\nТвоя ставка: {tmp[0][2]}\n" \
                            f"Победитель: {tmp[0][3]}\nРезультат: {tmp[0][4]}"
                        context.bot.send_message(chat_id=user_id[0], text=s)
                context.bot.send_message(chat_id=user_id[0], text='Результаты проставлены')

    def initialization_bot(self):
        self.tennis_DB = TennisDataBase(config.tennis_DB)
        dispatcher = self.updater.dispatcher

        jq = self.updater.job_queue
        jq.run_daily(self.message, datetime.time(9))
        jq.run_daily(self.autocheck, datetime.time(19, 45, 40))

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)

        answers_handler = CallbackQueryHandler(self.answers)
        dispatcher.add_handler(answers_handler)

        check_handler = CommandHandler('check', self.check)
        dispatcher.add_handler(check_handler)

        stats_handler = CommandHandler('stats', self.stats)
        dispatcher.add_handler(stats_handler)

    def start_bot(self):
        self.updater.start_polling()
        self.updater.idle()


bot = MainClass()
bot.initialization_bot()
bot.start_bot()


