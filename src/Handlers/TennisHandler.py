import datetime
from src.Handlers.SportHandler import SportHandler
from src.Sports.Tennis import Tennis


class TennisHandler(SportHandler):

    def sport(self, update, context, match_info, sport_data, sport):
        if (datetime.datetime.now() - datetime.timedelta(hours=8)).date() != sport_data.get_date():
            sport_data = Tennis()
        return super().sport(update, context, match_info, sport_data, sport)

    def autocheck(self, context, sport_data, sport_db):
        for key, value in sport_data.get_id().items():
            response = self.get_data(value)
            for user_id in sport_db.get_users():
                for elem in response:
                    data = {'match_id': elem['EVENT_ID']}
                    if elem['WINNER'] == 1:
                        data['winner'] = elem['HOME_NAME']
                    else:
                        data['winner'] = elem['AWAY_NAME']
                    tmp = sport_db.set_autocheck(data, user_id[0])
                    if len(tmp) > 0:
                        s = f"Результат проставлен\nМатч: {tmp[0][0]} - {tmp[0][1]}\nТвоя ставка: {tmp[0][2]}\n" \
                            f"Победитель: {tmp[0][3]}\nРезультат: {tmp[0][4]}"
                        context.bot.send_message(chat_id=user_id[0], text=s)
                context.bot.send_message(chat_id=user_id[0], text='Результаты проставлены')
