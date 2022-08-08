from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import Sports
import config
import datetime

import src.Sports.Tennis

match_info = {}
check_info = {}
last_tennis_date = datetime.date.today()
tennis_data = src.Sports.Tennis.Tennis()


def start(update, context):
    buttons = [[InlineKeyboardButton(text='Баскетбол', callback_data='basketball'),
               InlineKeyboardButton(text='Теннис', callback_data='tennis'),
               InlineKeyboardButton(text='Футбол', callback_data='football')]]
    menu = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери вид спорта', reply_markup=menu)


def echo(update, context):
    text = 'ECHO: ' + update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def answers(update, context):
    data = update.callback_query.data
    if data == 'basketball':
        basketball(update, context)
    elif data == 'tennis':
        tennis(update, context)
    elif data == 'football':
        football(update, context)


def basketball(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='basketball')


def tennis(update, context):
    global tennis_data
    match_info['kind_of_sport'] = 'tennis'
    match_info['user'] = update.effective_chat.id
    if datetime.date.today() != tennis_data.get_date():
        tennis_data = Sports.Tennis.Tennis()
    if update.effective_chat.id not in tennis_data.get_users():
        tennis_data.add_user(update.effective_chat.id)
    buttons = []
    for key in tennis_data.get_matches(update.effective_chat.id).keys():
        buttons.append([InlineKeyboardButton(text=key, callback_data=key)])
    buttons.append([InlineKeyboardButton(text='Вернуться к видам спорта', callback_data='back')])
    tennis_tournaments = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери турнир', reply_markup=tennis_tournaments)


def football(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='football')


updater = Updater(token=config.token, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

answers_handler = CallbackQueryHandler(answers)
dispatcher.add_handler(answers_handler)

updater.start_polling()
updater.idle()
