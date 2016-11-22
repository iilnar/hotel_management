import MySQLdb
from MySQLdb.cursors import DictCursor

import models


class DB:
    def __init__(self):
        self.db = MySQLdb.connect(host='localhost', user='root', passwd='password', db='hoteldb')

    def commit(self):
        self.db.commit()

    def query(self, query, one=False):
        c = self.db.cursor(cursorclass=DictCursor)
        c.execute(query)
        if not query.lower().startswith("select"):
            self.db.commit()
            return
        res = c.fetchall()
        if len(res) == 0:
            return None
        return (res[0] if res else None) if one else res

    def get_manager(self, login: str = None, id: int = None):
        if login is not None:
            return models.Manager(self.query('SELECT * FROM manager JOIN staff WHERE login = "%s"' % login, one=True))
        elif id is not None:
            return models.Manager(self.query('SELECT * FROM manager JOIN staff WHERE sid = "%s"' % id, one=True))

    def get_all_staff(self, hotel_id):
        q = self.query("SELECT * FROM staff WHERE hid = %s" % hotel_id)
        if q is None:
            q = []
        return [models.Staff(x) for x in q]

    def get_staff(self, id: int):
        return models.Staff(self.query("SELECT * from staff WHERE passport = %s" % id, one=True))

    def get_bookings(self, param):
        q = self.query('SELECT * FROM booking, room WHERE room.hid = %s AND booking.rid = room.id' % param)
        if q is None:
            q = []
        return [models.Booking(x) for x in q]

    def get_hotel(self, id: int):
        return models.Hotel(self.query('SELECT * FROM hotel WHERE id = %s' % id, one=True))

    def get_all_hotels(self):
        return [models.Hotel(x) for x in self.query('SELECT * from hotel')]

    def update_staff(self, staff: models.Staff):
        self.query('UPDATE staff SET %s WHERE passport = %s' % (staff.to_sql(), staff.passport))

    def remove_staff(self, staff: models.Staff):
        self.query('DELETE from staff WHERE passport = %s' % staff.passport)

    def check_city(self, name: str):
        return self.query('SELECT * from hotel WHERE city LIKE "%s"' % name) is not None

    def rin(self, city, check_in, check_out):
        q = self.query('SELECT * from hotel where id IN ('
                       'SELECT hid from room r where r.id NOT IN('
                       'SELECT r.id from room r, booking b WHERE b.rid = r.id AND (b.check_in > "%s" AND '
                       'b.check_in > "%s" OR b.check_out < "%s" AND b.check_out < "%s"))) AND city LIKE "%s"' % (check_in, check_out, check_out, check_in, city))
        if q is None:
            q = []
        return [models.Hotel(x) for x in q]

    def get_rooms(self, id):
        q = self.query('SELECT * from room JOIN room_category WHERE hid = %s' % id)
        if q is None:
            q = []
        return [models.Room(x) for x in q]

    def insert_booking(self, b: models.Booking):
        self.query('INSERT into booking (rid, uid, check_in, check_out, money) VALUES (%s, %s, "%s", "%s", %s)' % (b.room_id, b.user_id, b.check_in_date, b.check_out_date, b.money))

    def add_user_if_exists(self, user: models.User):
        r = self.query('SELECT id from users WHERE id = %s' % user.id, one=True)
        if r is None:
            self.query('INSERT into users (id, first_name, last_name) VALUES (%s, "%s", "%s")' % (user.id, user.first_name, user.last_name))

    def get_booking(self, id):
        return models.Booking(self.query('SELECT * from booking WHERE id=%s' % id, one=True))

    def update_booking(self, book: models.Booking):
        return self.query('UPDATE booking SET status = %s WHERE id = %s' % (book.status, book.id))

    def get_user(self, id):
        return models.User(self.query('SELECT * from users WHERE id=%s' % id, one=True))

    def get_room(self, id):
        return models.Room(self.query('SELECT * FROM room JOIN room_category WHERE room.id = %s' % id, one=True))

    def get_orders(self, chat_id):
        q = self.query('SELECT * FROM booking WHERE uid = %s' % chat_id)
        if q is None:
            q = []
        return [models.Booking(x) for x in q]

    def remove_booking(self, booking_id):
        self.query('DELETE FROM booking WHERE id=%s' % booking_id)

    def get_rooms_by_type(self, hotel_id, type):
        q = self.query('SELECT * FROM room JOIN room_category WHERE hid = %s AND type="%s"' % (hotel_id, type))
        if q is None:
            q = []
        return [models.Room(x) for x in q]

    def get_room_types(self, hotel_id):
        q = self.query('SELECT DISTINCT type FROM room_category WHERE id IN (SELECT rcid FROM room WHERE hid = %s)' % hotel_id)
        if q is None:
            q = []
        return [x['type'] for x in q]

    def add_staff(self, staff: models.Staff):
        self.query('INSERT into staff(passport, salary, first_name, last_name, position, hid) VALUES (%s, %s, "%s", "%s", "%s", %s)' % (staff.passport, staff.salary, staff.first_name, staff.last_name, staff.position, staff.hotel_id))
