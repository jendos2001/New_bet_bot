import datetime
import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class SportHandler:

    def sport(self, update, context, match_info, sport_data, sport):
        match_info['kind_of_sport'] = sport
        match_info['user'] = update.effective_chat.id
        if update.effective_chat.id not in sport_data.get_users():
            sport_data.add_user(update.effective_chat.id)
        buttons = []
        for key in sport_data.get_matches(update.effective_chat.id).keys():
            buttons.append([InlineKeyboardButton(text=key, callback_data=key)])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спорта', callback_data='back')])
        sport_tournaments = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери турнир',
                                 reply_markup=sport_tournaments)
        return match_info, sport_data

    @staticmethod
    def sport_matches(update, context, match_info, sport, sport_data, tmp_tournament=None):
        if tmp_tournament is None:
            data = update.callback_query.data
        else:
            data = tmp_tournament
        match_info['tournament'] = data
        match_info['tournament_id'] = sport_data.get_id()[data]
        buttons = []
        for key, value in sport_data.get_matches(update.effective_chat.id)[data].items():
            if 'round' in value.keys():
                text = f"{value['teams']} - {value['round']}"
            else:
                text = f"{value['teams']}"
            buttons.append([InlineKeyboardButton(text=text, callback_data=key)])
        if len(sport_data.get_matches(update.effective_chat.id)[data].items()) == 0:
            s = 'Все матчи этого турнира проставлены'
        else:
            s = 'Выбери матч'
        buttons.append([InlineKeyboardButton(text='Вернуться к турнирам', callback_data=f"{sport}")])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спорта', callback_data='back')])
        matches = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text=s, reply_markup=matches)
        return match_info

    @staticmethod
    def sport_match(update, context, match_info, sport_data):
        data = update.callback_query.data
        match_info['match'] = data
        match = sport_data.get_matches(update.effective_chat.id)[match_info['tournament']][data]['teams'].split(' - ')
        buttons = [[InlineKeyboardButton(text=match[0], callback_data=match[0])],
                   [InlineKeyboardButton(text=match[1], callback_data=match[1])]]
        current_match = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери победителя', reply_markup=current_match)
        return match_info

    @staticmethod
    def sport_add_match(update, context, match_info, sport_data, sport, sport_DB):
        data = {'user_id': match_info['user'],
                'match_date': str(datetime.date.today()),
                'tournament': match_info['tournament'],
                'round': sport_data.get_matches(update.effective_chat.id)[
                    match_info['tournament']][match_info['match']]['round'],
                'year': datetime.datetime.now().year,
                'match_id': sport_data.get_matches(update.effective_chat.id)[
                    match_info['tournament']][match_info['match']]['match_id'],
                'team1': sport_data.get_matches(update.effective_chat.id)[
                    match_info['tournament']][match_info['match']]['teams'].split(' - ')[0],
                'team2': sport_data.get_matches(update.effective_chat.id)[
                    match_info['tournament']][match_info['match']]['teams'].split(' - ')[1],
                'bet': match_info['bet'], 'tournament_id': match_info['tournament_id']}
        sport_data.delete_match(update.effective_chat.id, match_info['tournament'], match_info['match'])
        sport_DB.add_data(data)
        buttons = [[InlineKeyboardButton(text='Продолжить', callback_data=f'back_{sport}_matches')]]
        continue_add = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Матч добавлен', reply_markup=continue_add)

    @staticmethod
    def sport_check(update, context, match_info, sport_data, sport, data):
        match_info['bet'] = data
        s = "Проверь ставку:\nТеннис: {}\nСтавка: {}".format(sport_data.get_matches(
            update.effective_chat.id)[match_info['tournament']][match_info['match']]['teams'], match_info['bet'])
        buttons = [[InlineKeyboardButton(text='Да, всё верно', callback_data=f'{sport}_add_match')],
                   [InlineKeyboardButton(text='Нет, вернуться к матчам', callback_data=f'back_{sport}_matches')],
                   [InlineKeyboardButton(text='Нет, вернуться к турнирам',
                                         callback_data=f'back_{sport}_tournaments')]]
        sport_confirm = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text=s, reply_markup=sport_confirm)
        return match_info

    @staticmethod
    def sport_stats(update, context, stats_info, sport, sport_db):
        stats_info['sport'] = sport
        buttons = []
        for elem in sport_db.get_years():
            text = str(elem[0])
            data = f"{elem[0]} - {sport}_stats"
            buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спортам со статистикой',
                                             callback_data='back_stats')])
        years = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери год',
                                 reply_markup=years)
        return stats_info

    @staticmethod
    def sport_tournaments(update, context, stats_info, sport, sport_db):
        stats_info['year'] = int(update.callback_query.data.split(' - ')[0])
        buttons = []
        for elem in sport_db.get_tournaments_by_year(stats_info['year']):
            text = str(elem[0])
            data = f"{elem[0]} - {sport}_stats"
            buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спортам со статистикой',
                                             callback_data='back_stats')])
        years = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери турнир',
                                 reply_markup=years)
        return stats_info

    @staticmethod
    def get_stats(update, context, stats_info, sport_db):
        stats_info['tournament'] = update.callback_query.data.split(' - ')[0]
        buttons = []
        results = sport_db.get_stats(stats_info)
        plus = u'\U00002705'
        minus = u'\U0000274C'
        s = f"{stats_info['tournament']} - {stats_info['year']}\n{plus}{results[0][0]}" \
            f"\n{minus}{results[1][0]}"
        buttons.append([InlineKeyboardButton(text='Вернуться к видам спортам со статистикой',
                                             callback_data='back_stats')])
        stats = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=update.effective_chat.id, text=s,
                                 reply_markup=stats)
        return stats_info

    @staticmethod
    def get_data(value):
        url = "https://flashscore.p.rapidapi.com/v1/tournaments/results"
        querystring = {"locale": "en_GB", "tournament_stage_id": value, "page": "1"}
        headers = {
            "X-RapidAPI-Key": "97e3e90f2dmsh490b0ed8c6df919p1c5460jsn31ae902c52e8",
            "X-RapidAPI-Host": "flashscore.p.rapidapi.com"
        }
        return requests.request("GET", url, headers=headers, params=querystring).json()['DATA'][0]['EVENTS']

    def autocheck(self, context, sport_data, sport_db):
        pass
