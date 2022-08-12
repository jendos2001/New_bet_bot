from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config
import datetime
import Sports.Tennis
from DB.tennisDB import TennisDataBase
from Handlers.TennisHandler import TennisHandler


class MainClass:
    tennis_DB = None

    def __init__(self):
        self.match_info = {}
        self.check_info = {}
        self.stats_info = {}
        self.tennis_data = Sports.Tennis.Tennis()
        self.tennis_handler = TennisHandler()
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
            self.match_info = self.tennis_handler.sport_check(update, context, self.match_info, self.tennis_data,
                                                              'tennis', data)

    def answers(self, update, context):
        self.check_bet(update, context)
        data = update.callback_query.data
        if data == 'basketball':
            self.basketball(update, context)
        elif data == 'tennis':
            self.match_info, self.tennis_data = \
                self.tennis_handler.sport(update, context, self.match_info, self.tennis_data, data)
        elif data == 'football':
            self.football(update, context)
        elif data == 'back_stats':
            self.stats_info.clear()
            self.stats(update, context)
        elif data == 'basketball_stats':
            self.basketball_stats(update, context)
        elif data == 'tennis_stats':
            self.stats_info = self.tennis_handler.sport_stats(update, context, self.stats_info, 'tennis',
                                                              TennisDataBase(config.tennis_DB))
        elif data.split(' - ')[0].isnumeric() and data.split(' - ')[1] == 'tennis_stats':
            self.stats_info = self.tennis_handler.sport_tournaments(update, context, self.stats_info, 'tennis',
                                                                    TennisDataBase(config.tennis_DB))
        elif len(data.split(' - ')) == 2 and data.split(' - ')[1] == 'tennis_stats':
            self.stats_info = self.tennis_handler.get_stats(update, context, self.stats_info,
                                                            TennisDataBase(config.tennis_DB))
        elif data == 'football_stats':
            self.football_stats(update, context)
        elif data in self.tennis_data.get_matches(update.effective_chat.id).keys():
            self.match_info = self.tennis_handler.sport_matches(update, context, self.match_info, 'tennis',
                                                                self.tennis_data)
        elif data in self.tennis_data.get_matches(update.effective_chat.id)[self.match_info['tournament']].keys():
            self.match_info = self.tennis_handler.sport_match(update, context, self.match_info, self.tennis_data)
        elif data == 'back':
            self.match_info.clear()
            self.start(update, context)
        elif data == 'back_tennis_tournaments':
            self.match_info.clear()
            self.match_info['kind_of_sport'] = 'tennis'
            self.match_info['user'] = update.effective_chat.id
            self.match_info, self.tennis_data = \
                self.tennis_handler.sport(update, context, self.match_info, self.tennis_data, data)
        elif data == 'back_tennis_matches':
            tmp_tournament = self.match_info['tournament']
            tmp_sport = self.match_info['kind_of_sport']
            self.match_info.clear()
            self.match_info['tournament'] = tmp_tournament
            self.match_info['kind_of_sport'] = tmp_sport
            self.match_info['user'] = update.effective_chat.id
            self.match_info = self.tennis_handler.sport_matches(update, context, self.match_info, 'tennis',
                                                                self.tennis_data, tmp_tournament)
        elif data == 'tennis_add_match':
            self.tennis_handler.sport_add_match(update, context, self.match_info, self.tennis_data, 'tennis',
                                                TennisDataBase(config.tennis_DB))

    def basketball(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='basketball')

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

    @staticmethod
    def message(context):
        db = TennisDataBase(config.tennis_DB)
        for elem in db.get_users():
            context.bot.send_message(chat_id=elem[0], text='Не пора ли проставить матчи?')

    def autocheck(self, context):
        self.tennis_handler.autocheck(context, self.tennis_data, TennisDataBase(config.tennis_DB))

    def initialization_bot(self):
        dispatcher = self.updater.dispatcher

        jq = self.updater.job_queue
        jq.run_daily(self.message, datetime.time(9))
        jq.run_daily(self.autocheck, datetime.time(10, 30))

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)

        answers_handler = CallbackQueryHandler(self.answers)
        dispatcher.add_handler(answers_handler)

        stats_handler = CommandHandler('stats', self.stats)
        dispatcher.add_handler(stats_handler)

    def start_bot(self):
        self.updater.start_polling()
        self.updater.idle()


bot = MainClass()
bot.initialization_bot()
bot.start_bot()
