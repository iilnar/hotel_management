#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

import datetime

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardHide
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Updater, CommandHandler
from emoji import emojize
import logging
import telegram

import utils
from utils import months, days, parse_month, parse_date, unshared_copy, dict_to_str, hotels

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
API_TOKEN = '290052223:AAEMmqxdt6dB3ntqGJD9M74UPy6lB4qcJdA'

CHOOSING, TYPING_DATE, TYPING_REPLY = range(3)
HOTEL_VIEW, ROOM_VIEW, BOOK_VIEW = range(3)

CITY_TAG = 'city'
CHECK_IN_TAG = 'check_in'
CHECK_OUT_TAG = 'check_out'
UNDEFINED_TAG = 'undefined_tag'
MONTH_TAG = 'month_tag'
CHOICE_TAG = 'choice'
CANCEL_TAG = 'cancel'
STATUS_TAG = 'status'

HOTELS_LIST = 'hotels_list'
ROOMS_LIST = 'rooms_list'
HOTEL_ID = 'id'
ROOM_ID = 'room_id'
STAR = emojize(':star:', use_aliases=True)

reply_keyboard_template = [[CITY_TAG.capitalize()],
                           [CHECK_IN_TAG.capitalize(), CHECK_OUT_TAG.capitalize()],
                           ['Search hotels'],
                           [CANCEL_TAG.capitalize()]]

queries = {}

markup = ReplyKeyboardMarkup(reply_keyboard_template, one_time_keyboard=True)

month_markup = ReplyKeyboardMarkup([months[1:4],
                                    months[4:7],
                                    months[7:10],
                                    months[10:13],
                                    [CANCEL_TAG.capitalize()]], one_time_keyboard=True)


def get_reply_keyboard_markup(user_data):
    reply_keyboard = unshared_copy(reply_keyboard_template)  # type: list[list[str]]
    if user_data is not None:
        for key in user_data:  # type: str
            if key == CITY_TAG:
                reply_keyboard[0][0] = reply_keyboard[0][0] + ': ' + user_data[CITY_TAG]
            if key == CHECK_IN_TAG:
                reply_keyboard[1][0] = reply_keyboard[1][0] + ': ' + user_data[CHECK_IN_TAG]
            if key == CHECK_OUT_TAG:
                reply_keyboard[1][1] = reply_keyboard[1][1] + ': ' + user_data[CHECK_OUT_TAG]

    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def get_day_select_keyboard_markup(month: int):
    days_count = days[month]
    return ReplyKeyboardMarkup([[str(x) for x in range(1, 8)],
                                [str(x) for x in range(8, 15)],
                                [str(x) for x in range(15, 22)],
                                [str(x) for x in range(22, 29)],
                                [str(x) for x in range(29, days_count)],
                                [CANCEL_TAG.capitalize()]], one_time_keyboard=True)


def start(bot: telegram.Bot, update: telegram.Update):
    msg = update.message  # type: telegram.Message
    msg.reply_text("Hi, please fill your query", reply_markup=markup)

    return CHOOSING


def choice(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    tag = get_tag(msg.text)
    if tag == UNDEFINED_TAG:
        msg.reply_text('I dind\'t understand you.', reply_markup=get_reply_keyboard_markup(user_data))
        return CHOOSING
    user_data[CHOICE_TAG] = tag
    if tag == CHECK_IN_TAG or tag == CHECK_OUT_TAG:
        msg.reply_text('Please select month', reply_markup=month_markup)
        return TYPING_DATE
    msg.reply_text('Please, select your ' + tag)

    return TYPING_REPLY


def get_tag(msg: str):
    if re.match('(?i)city', msg):
        return CITY_TAG
    if re.match('(?i)check.*in', msg):
        return CHECK_IN_TAG
    if re.match('(?i)check.*out', msg):
        return CHECK_OUT_TAG
    return UNDEFINED_TAG


def received_information(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    if msg.text.lower() == CANCEL_TAG:
        msg.reply_text("Please fill your query", reply_markup=markup)
        return CHOOSING
    category = user_data[CHOICE_TAG].lower()
    user_data[category] = msg.text
    del user_data[CHOICE_TAG]
    msg.reply_text('Here\'s your query', reply_markup=get_reply_keyboard_markup(user_data))
    return CHOOSING


def receive_date(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    if msg.text.lower() == CANCEL_TAG:
        if MONTH_TAG in user_data:
            del user_data[MONTH_TAG]
        msg.reply_text("Please fill your query", reply_markup=markup)
        return CHOOSING

    if MONTH_TAG not in user_data:
        month = parse_month(msg.text)
        if month < 1 or month > 12:
            msg.reply_text('Please select month', reply_markup=month_markup)
            return TYPING_DATE
        user_data[MONTH_TAG] = month
        msg.reply_text('Please select day', reply_markup=get_day_select_keyboard_markup(month))
        return TYPING_DATE
    month = user_data[MONTH_TAG]

    try:
        today = datetime.date.today()
        day = int(msg.text)
        date = datetime.date(today.year, month, day)
        if date < today:
            date = datetime.date(today.year + 1, month, day)
        if user_data[CHOICE_TAG] == CHECK_IN_TAG:
            if CHECK_OUT_TAG in user_data:
                if date >= parse_date(user_data[CHECK_OUT_TAG]):
                    del user_data[CHECK_OUT_TAG]
            user_data[CHECK_IN_TAG] = date.isoformat()
        if user_data[CHOICE_TAG] == CHECK_OUT_TAG:
            if CHECK_IN_TAG in user_data:
                if date <= parse_date(user_data[CHECK_IN_TAG]):
                    raise ValueError()
            user_data[CHECK_OUT_TAG] = date.isoformat()
        del user_data[CHOICE_TAG]
    except ValueError:
        msg.reply_text('Please select day', reply_markup=get_day_select_keyboard_markup(month))
        return TYPING_DATE

    del user_data[MONTH_TAG]
    msg.reply_text('Here\'s your query', reply_markup=get_reply_keyboard_markup(user_data))
    return CHOOSING


def search(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    if CHOICE_TAG in user_data:
        del user_data[CHOICE_TAG]
    # msg.reply_text('Here\' your query: %s' % dict_to_str(user_data), reply_markup=ReplyKeyboardHide(True))
    check_in = user_data[CHECK_IN_TAG] if CHECK_IN_TAG in user_data else ''
    check_out = user_data[CHECK_OUT_TAG] if CHECK_OUT_TAG in user_data else ''
    city = user_data[CITY_TAG] if CITY_TAG in user_data else ''
    show(update, check_in, check_out, city)
    user_data.clear()
    return ConversationHandler.END


PREV = 'prev'
NEXT = 'next'
INFO = 'info'
BACK = 'back'
BOOK = 'book'
FILTER = 'filter'
SORT = 'sort'

hotel_keyboard_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(PREV.capitalize(), callback_data=PREV),
     InlineKeyboardButton(NEXT.capitalize(), callback_data=NEXT)],
    [InlineKeyboardButton(INFO.capitalize(), callback_data=INFO)],
    [InlineKeyboardButton(FILTER.capitalize(), callback_data=FILTER),
     InlineKeyboardButton(SORT.capitalize(), callback_data=SORT)],
    [InlineKeyboardButton(BACK.capitalize(), callback_data=BACK)]
])

room_keyboard_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(PREV.capitalize(), callback_data=PREV),
     InlineKeyboardButton(NEXT.capitalize(), callback_data=NEXT)],
    [InlineKeyboardButton(BOOK.capitalize(), callback_data=BOOK)],
    [InlineKeyboardButton(BACK.capitalize(), callback_data=BACK)]
])


def show(update: telegram.Update, check_in: str, check_out: str, city: str):
    query = {
        CHECK_IN_TAG: check_in,
        CHECK_OUT_TAG: check_out,
        CITY_TAG: city,
        HOTELS_LIST: hotels,  # type [utils.Hotel]
        HOTEL_ID: 0,
        ROOM_ID: 0,
        STATUS_TAG: HOTEL_VIEW
    }
    queries[update.message.chat_id] = query
    update.message.reply_text(disable_web_page_preview=False,
                              text=prettify_hotel(query[HOTELS_LIST][0]),
                              parse_mode=telegram.ParseMode.HTML,
                              reply_markup=hotel_keyboard_markup)


def prettify_hotel(hotel: utils.Hotel):
    res = '<b>%s</b>\n' % hotel.name
    for i in range(hotel.stars):
        res += STAR
    res += '\n'
    res += '<a href="%s">.</a>' % hotel.img
    return res


def prettify_room(room: utils.Room):
    res = 'Type: %s\n' % room.type
    res += 'Cost: %s RUB\n' % room.price
    res += '<a href="%s">.</a>' % room.img
    return res


def show_hotel(bot: telegram.Bot, callback_query, hotel: utils.Hotel):
    bot.edit_message_text(
        chat_id=callback_query.message.chat_id,
        message_id=callback_query.message.message_id,
        disable_web_page_preview=False,
        text=prettify_hotel(hotel),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=hotel_keyboard_markup
    )


def show_room(bot: telegram.Bot, callback_query, room: utils.Room):
    bot.edit_message_text(
        chat_id=callback_query.message.chat_id,
        message_id=callback_query.message.message_id,
        disable_web_page_preview=False,
        text=prettify_room(room),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=room_keyboard_markup
    )


def button(bot: telegram.Bot, update: telegram.Update):
    callback_query = update.callback_query  # type: telegram.CallbackQuery
    query = queries[callback_query.message.chat_id]
    op = callback_query.data.lower()
    if op == PREV or op == NEXT:
        if query[STATUS_TAG] == HOTEL_VIEW:
            new_id = query[HOTEL_ID] - 1 if op == PREV else query[HOTEL_ID] + 1
            if 0 <= new_id < len(query[HOTELS_LIST]):
                query[HOTEL_ID] = new_id
            show_hotel(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]])
        else:
            new_id = query[ROOM_ID] - 1 if op == PREV else query[ROOM_ID] + 1
            if 0 <= new_id < len(query[HOTELS_LIST][query[HOTEL_ID]].rooms):
                query[ROOM_ID] = new_id
            show_room(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]].rooms[query[ROOM_ID]])
    elif op == INFO:
        query[ROOM_ID] = 0
        query[STATUS_TAG] = ROOM_VIEW
        show_room(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]].rooms[query[ROOM_ID]])
    elif op == BACK:
        if query[STATUS_TAG] == ROOM_VIEW:
            query[STATUS_TAG] = HOTEL_VIEW
            del query[ROOM_ID]
            show_hotel(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]])


def main():
    bot = telegram.Bot(token=API_TOKEN)
    updater = Updater(token=API_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [RegexHandler('(?i)city|check.*in|check.*out', choice, pass_user_data=True)],
            TYPING_DATE: [MessageHandler(Filters.text, receive_date, pass_user_data=True)],
            TYPING_REPLY: [MessageHandler(Filters.text, received_information, pass_user_data=True)]
        },
        fallbacks=[RegexHandler('(?i)^Search*', search, pass_user_data=True),
                   CommandHandler('stop', search, pass_user_data=True)]
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()


if __name__ == '__main__':
    main()
