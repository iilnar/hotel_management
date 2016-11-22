import telegram
from flask import Flask, g
from flask import _app_ctx_stack
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import bot
import db
import models

SECRET_KEY = 'MR'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_db() -> db.DB:
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = db.DB()
    return top.db


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('hotel_info', hotel_id=g.user.hotel_id))
    error = None
    if request.method == 'POST':
        user = get_db().get_manager(request.form['login'])
        if user is None:
            error = 'No such user'
        elif user.password != request.form['password']:  # TODO change to hash
            error = 'Wrong password'
        else:
            flash('You\'re now logged in')
            session['user_id'] = user.id
            g.user = user
            return redirect(url_for('hotel_info', hotel_id=user.hotel_id))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    flash('You were logged out')
    session.pop('user_id')
    return redirect(url_for('login'))


@app.route('/bookings/<hotel_id>')
def bookings(hotel_id):
    error = None
    hotel = get_db().get_hotel(hotel_id)
    if not check_permission(hotel=hotel):
        return redirect(url_for('login'))

    bookings = get_db().get_bookings(hotel_id)
    for booking in bookings:
        user = get_db().get_user(booking.user_id)
        booking.user = (user.first_name + ' ' + user.second_name)
    return render_template('bookings.html', bookings=bookings)


@app.route('/hotel_info/<hotel_id>')
def hotel_info(hotel_id):
    hotel = get_db().get_hotel(hotel_id)
    if not check_permission(hotel=hotel):
        return redirect(url_for('login'))

    staff = get_db().get_all_staff(hotel_id)
    return render_template('hotel_info.html', hotel=hotel, staff=staff)


@app.route('/')
def empty():
    return redirect(url_for('login'))


@app.route('/staff/<hotel_id>')
def staff(hotel_id):
    hotel = get_db().get_hotel(hotel_id)
    if not check_permission(hotel=hotel):
        return redirect(url_for('login'))

    staff = get_db().get_all_staff(hotel_id)
    return render_template('staff.html', hotel=hotel, staff=staff)


@app.route('/staff_info/<staff_passport>', methods=['GET', 'POST'])
def staff_info(staff_passport=None):
    staff = None
    if staff_passport is not None:
        staff = get_db().get_staff(staff_passport)
    return render_template('staff_info.html', staff=staff, is_new=False)


@app.route('/new_staff', methods=['GET', 'POST'])
def new_staff():
    return render_template('staff_info.html', staff=models.Staff(''), is_new=True)


@app.route('/remove_staff/<staff_passport>', methods=['GET', 'POST'])
def remove_staff(staff_passport):
    staff = get_db().get_staff(staff_passport);
    if not check_permission(staff=staff):
        return redirect(url_for('login'))
    return render_template(url_for('staff_list', hotel_id=g.user.hotel_id))


@app.route('/update_staff/<staff_passport>', methods=['GET', 'POST'])
def update_staff(staff_passport):
    if request.method == 'POST':
        staff = models.Staff(request.form)
        staff.hotel_id = g.user.hotel_id
        if staff_passport != 0:
            staff.passport = staff_passport
        if staff_passport == 0:
            get_db().add_staff(staff)
        else:
            get_db().update_staff(staff)
    return redirect(url_for('hotel_info', hotel_id=g.user.hotel_id))


@app.route('/cancel_booking/<booking_id>')
def cancel_booking(booking_id):
    booking = get_db().get_booking(booking_id)
    user = get_db().get_user(booking.user_id)

    if not check_permission(hotel=get_db().get_hotel(get_db().get_room(booking.room_id))):
        return redirect(url_for('login'))

    bo = telegram.Bot(bot.API_TOKEN)
    bo.sendMessage(
        chat_id=user.id,
        text="Sorry, your reservation #%s has been cancelled" % booking_id
    )
    get_db().remove_booking(booking_id)
    return redirect(url_for('bookings', hotel_id=get_db().get_room(booking.room_id).hotel_id))


@app.route('/approve_booking/<booking_id>')
def approve_booking(booking_id):
    booking = get_db().get_booking(booking_id)
    user = get_db().get_user(booking.user_id)

    if not check_permission(hotel=get_db().get_hotel(get_db().get_room(booking.room_id))):
        return redirect(url_for('login'))

    bo = telegram.Bot(bot.API_TOKEN)
    bo.sendMessage(
        chat_id=user.id,
        text="Your booking #%s has been approved by administrator. See you on %s :)" % (booking_id, booking.check_in_date)
    )
    hotel_id = get_db().get_room(booking.room_id).hotel_id
    return redirect(url_for('bookings', hotel_id=hotel_id))


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = get_db().get_manager(id=session['user_id'])


def check_permission(hotel: models.Hotel = None, staff: models.Staff = None):
    if g.user is None:
        return False
    id = None
    if hotel is not None:
        id = hotel.id
    if staff is not None:
        id = staff.hotel_id
    return id == g.user.hotel_id


if __name__ == '__main__':
    app.run()
