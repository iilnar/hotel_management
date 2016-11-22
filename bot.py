#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

import datetime

import db
import en as loc

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
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

import models
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

HOTELS_LIST = 'hotels_list'
ROOMS_LIST = 'rooms_list'
HOTEL_ID = 'id'
ROOM_ID = 'room_id'
MESSAGE_ID = 'message_id'
STAR = emojize(':star:', use_aliases=True)

reply_keyboard_template = [[loc.CITY],
                           [loc.CHECK_IN, loc.CHECK_OUT],
                           [loc.SEARCH],
                           [loc.CANCEL]]

reply_keyboard_menu_template = [
    [loc.NEW_SEARCH],
    [loc.BOOKING_HISTORY],
    [loc.CANCEL]
]

queries = {}

markup = ReplyKeyboardMarkup(reply_keyboard_template, one_time_keyboard=True)

menu_markup = ReplyKeyboardMarkup(reply_keyboard_menu_template, one_time_keyboard=True)

month_markup = ReplyKeyboardMarkup([months[1:4],
                                    months[4:7],
                                    months[7:10],
                                    months[10:13],
                                    [loc.CANCEL]], one_time_keyboard=True)


def get_reply_keyboard_markup(user_data=None):
    reply_keyboard = unshared_copy(reply_keyboard_template)  # type: list[list[str]]
    if user_data is not None:
        if CITY_TAG in user_data:
            reply_keyboard[0][0] = reply_keyboard[0][0] + ': ' + user_data[CITY_TAG]
        if CHECK_IN_TAG in user_data:
            reply_keyboard[1][0] = reply_keyboard[1][0] + ': ' + user_data[CHECK_IN_TAG]
        if CHECK_OUT_TAG in user_data:
            reply_keyboard[1][1] = reply_keyboard[1][1] + ': ' + user_data[CHECK_OUT_TAG]

    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def get_day_select_keyboard_markup(month: int):
    days_count = days[month]
    return ReplyKeyboardMarkup([[str(x) for x in range(1, 8)],
                                [str(x) for x in range(8, 15)],
                                [str(x) for x in range(15, 22)],
                                [str(x) for x in range(22, 29)],
                                [str(x) for x in range(29, days_count)],
                                [loc.CANCEL]], one_time_keyboard=True)


def show_query(update: telegram.Update, user_data=None):
    update.message.reply_text('Please, fill your query', reply_markup=get_reply_keyboard_markup(user_data))


def start(bot: telegram.Bot, update: telegram.Update):
    show_query(update)
    return CHOOSING


def get_tag(msg: str):
    if re.match('(?i)city', msg):
        return CITY_TAG
    if re.match('(?i)check.*in', msg):
        return CHECK_IN_TAG
    if re.match('(?i)check.*out', msg):
        return CHECK_OUT_TAG
    return UNDEFINED_TAG


def choice(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    tag = get_tag(msg.text)
    if tag == UNDEFINED_TAG:
        msg.reply_text('I don\'t understand you.', reply_markup=get_reply_keyboard_markup(user_data))
        return CHOOSING
    user_data[CHOICE_TAG] = tag
    if tag == CHECK_IN_TAG or tag == CHECK_OUT_TAG:
        msg.reply_text('Please select month', reply_markup=month_markup)
        return TYPING_DATE
    msg.reply_text('Please, select your ' + tag)

    return TYPING_REPLY


def received_information(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    if msg.text.lower() == loc.CANCEL:
        show_query(update, user_data)
        return CHOOSING
    category = user_data[CHOICE_TAG].lower()
    if category == CITY_TAG:
        city = msg.text
        if not db.DB().check_city(city):
            msg.reply_text("We don't have hotels in %s" % city, reply_markup=get_reply_keyboard_markup(user_data))
            return CHOOSING
    user_data[category] = msg.text
    del user_data[CHOICE_TAG]
    show_query(update, user_data)
    return CHOOSING


def receive_date(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    if msg.text.lower() == CANCEL_TAG:
        if MONTH_TAG in user_data:
            del user_data[MONTH_TAG]
        show_query(update)
        return CHOOSING

    if MONTH_TAG not in user_data:
        month = parse_month(msg.text)
        if month < 1 or month > 12:
            msg.reply_text('Invalid month, select another', reply_markup=month_markup)
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
        msg.reply_text('Invalid day, try again', reply_markup=get_day_select_keyboard_markup(month))
        return TYPING_DATE

    del user_data[MONTH_TAG]
    show_query(update, user_data)
    return CHOOSING


def search(bot: telegram.Bot, update: telegram.Update, user_data):
    msg = update.message  # type: telegram.Message
    if CHOICE_TAG in user_data:
        del user_data[CHOICE_TAG]

    if CITY_TAG not in user_data or CHECK_IN_TAG not in user_data or CHECK_OUT_TAG not in user_data:
        msg.reply_text('Fill all the fields', reply_markup=get_reply_keyboard_markup(user_data))
        return CHOOSING

    check_in = user_data[CHECK_IN_TAG] if CHECK_IN_TAG in user_data else ''
    check_out = user_data[CHECK_OUT_TAG] if CHECK_OUT_TAG in user_data else ''
    city = user_data[CITY_TAG] if CITY_TAG in user_data else ''

    show(update, check_in, check_out, city)
    user_data.clear()
    return ConversationHandler.END


HOTEL_PREV = 'hotel_prev'
HOTEL_NEXT = 'hotel_next'
HOTEL_INFO = 'hotel_info'
HOTEL_BACK = 'hotel_back'
HOTEL_LOCA = 'hotel_loca'

ROOM_PREV = 'room_prev'
ROOM_NEXT = 'room_next'
ROOM_BOOK = 'room_book'
ROOM_BACK = 'room_back'

LOCA_BACK = 'loca_back'

hotel_keyboard_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(loc.PREV, callback_data=HOTEL_PREV),
     InlineKeyboardButton(loc.NEXT, callback_data=HOTEL_NEXT)],
    [InlineKeyboardButton(loc.INFO, callback_data=HOTEL_INFO)],
    [InlineKeyboardButton(loc.LOCA, callback_data=HOTEL_LOCA)],
    [InlineKeyboardButton(loc.BACK, callback_data=HOTEL_BACK)]
])

room_keyboard_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(loc.PREV, callback_data=ROOM_PREV),
     InlineKeyboardButton(loc.NEXT, callback_data=ROOM_NEXT)],
    [InlineKeyboardButton(loc.BOOK, callback_data=ROOM_BOOK)],
    [InlineKeyboardButton(loc.BACK, callback_data=ROOM_BACK)]
])

loca_keyboard_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(loc.BACK, callback_data=LOCA_BACK)]
])


def show(update: telegram.Update, check_in: str, check_out: str, city: str):
    query = {
        CHECK_IN_TAG: check_in,
        CHECK_OUT_TAG: check_out,
        CITY_TAG: city,
        HOTELS_LIST: db.DB().rin(city, check_in, check_out),  # type [models.Hotel]
        HOTEL_ID: 0,
        ROOM_ID: 0
    }
    if len(query[HOTELS_LIST]) == 0:
        update.message.reply_text(
            text="Sorry, there's no hotels available"
        )
        return ConversationHandler.END
    for hotel in query[HOTELS_LIST]:
        hotel.rooms = db.DB().get_rooms(hotel.id)
    queries[update.message.chat_id] = query
    update.message.reply_text(
        disable_web_page_preview=False,
        text=prettify_hotel(query[HOTELS_LIST][0]),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=hotel_keyboard_markup
    )
    return ConversationHandler.END


def prettify_hotel(hotel: models.Hotel):
    res = '<b>%s</b>\n' % hotel.name
    for i in range(hotel.stars):
        res += STAR
    res += '\n'
    res += '<a href="%s">.</a>' % hotel.image_url
    return res


def prettify_room(room: models.Room):
    res = 'Type: %s\n' % room.room_type
    res += 'Cost: %s RUB\n' % room.price
    res += 'Parking: %s\n' % ('YES' if room.parking else 'NO')
    res += '<a href="%s">.</a>' % room.image_url
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
    op = callback_query.data

    if op == HOTEL_PREV or op == HOTEL_NEXT:
        hl = len(query[HOTELS_LIST])
        query[HOTEL_ID] = new_id = (query[HOTEL_ID] - (1 if op == HOTEL_PREV else -1) + hl) % hl
        show_hotel(bot, callback_query, query[HOTELS_LIST][new_id])

    if op == ROOM_PREV or op == ROOM_NEXT:
        rl = len(query[HOTELS_LIST][query[HOTEL_ID]].rooms)
        query[ROOM_ID] = new_id = (query[ROOM_ID] - (1 if op == ROOM_PREV else -1) + rl) % rl
        show_room(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]].rooms[new_id])

    if op == HOTEL_INFO:
        query[ROOM_ID] = 0
        show_room(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]].rooms[query[ROOM_ID]])

    if op == HOTEL_BACK:
        bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text='.'
        )
        menu(bot, callback_query)
    if op == HOTEL_LOCA:
        hotel = query[HOTELS_LIST][query[HOTEL_ID]]
        bot.edit_message_text(
            text=hotel.name,
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
        )
        query[MESSAGE_ID] = callback_query.message.message_id + 1
        bot.send_location(
            chat_id=callback_query.message.chat_id,
            reply_markup=loca_keyboard_markup,
            latitude=hotel.latitude,
            longitude=hotel.longitude
        )

    if op == LOCA_BACK:
        bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
        bot.send_message(
            chat_id=callback_query.message.chat_id,
            text=prettify_hotel(query[HOTELS_LIST][query[HOTEL_ID]]),
            disable_web_page_preview=False,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=hotel_keyboard_markup
        )

    if op == ROOM_BOOK:
        room = query[HOTELS_LIST][query[HOTEL_ID]].rooms[query[ROOM_ID]]  # type: models.Room
        user = callback_query.from_user  # type: telegram.User
        d = db.DB()
        d.add_user_if_exists(models.User({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name
        }))
        d.insert_booking(models.Booking({
            'rid': room.id,
            'uid': user.id,
            'check_in': query[CHECK_IN_TAG],
            'check_out': query[CHECK_OUT_TAG],
            'money': room.price
        }))
        bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text="Booked, we will approve soon:)",
        )
        menu(bot, callback_query)

    if op == ROOM_BACK:
        del query[ROOM_ID]
        show_hotel(bot, callback_query, query[HOTELS_LIST][query[HOTEL_ID]])


def bookings_list(bot: telegram.Bot, update: telegram.Update):
    bd = db.DB()
    d = bd.get_orders(update.message.chat_id)  # type: [models.Booking]
    s = ''
    for booking in d:
        room = bd.get_room(booking.room_id)
        hotel = bd.get_hotel(room.hotel_id)
        s += '<b>%s</b> "%s" from %s to %s\n' % (booking.id, hotel.name, booking.check_in_date, booking.check_out_date)
    if s == '':
        s = 'You don\'t have any bookings. Use "%s" for making your first book' % loc.NEW_SEARCH
    update.message.reply_text(
        text=s,
        parse_mode=telegram.ParseMode.HTML
    )


def cancel_booking(bot: telegram.Bot, update: telegram.Update):
    bd = db.DB()
    id = update.message.text.split()
    if len(id) <= 1:
        update.message.reply_text(
            text="Usage: cancel [booking id]"
        )
        return
    id = id[1]
    booking = bd.get_booking(id)
    res = 'It is not your reservation, shame on you!'
    if booking is None or booking.user_id == update.message.chat_id:
        bd.remove_booking(id)
        res = 'Your order has been cancelled'

    update.message.reply_text(
        text=res
    )


def menu(bot: telegram.Bot, update: telegram.Update, user_data=None):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Menu:',
        reply_markup=menu_markup
    )
    if user_data is not None:
        user_data.clear()


bot = telegram.Bot(token=API_TOKEN)


def main():
    updater = Updater(token=API_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[RegexHandler('(?i)New search', start)],
        states={
            CHOOSING: [RegexHandler('(?i)city|check.*in|check.*out', choice, pass_user_data=True)],
            TYPING_DATE: [MessageHandler(Filters.text, receive_date, pass_user_data=True)],
            TYPING_REPLY: [MessageHandler(Filters.text, received_information, pass_user_data=True)]
        },
        fallbacks=[RegexHandler('(?i)^Search*', search, pass_user_data=True),
                   CommandHandler('stop', menu, pass_user_data=True)]
    )

    orders_handler = RegexHandler('(?i)%s' % loc.BOOKING_HISTORY, bookings_list)
    start_handler = CommandHandler('start', menu)
    cancel_handler = RegexHandler('(?i)%s' % loc.CANCEL, cancel_booking)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(orders_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(cancel_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()


if __name__ == '__main__':
    main()
