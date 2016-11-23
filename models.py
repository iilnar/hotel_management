class Staff:
    def __init__(self, dict):
        if dict is None:
            dict = {}
        self.passport = int(dict['passport']) if 'passport' in dict else 0
        self.salary = int(dict['salary']) if 'salary' in dict else 0
        self.first_name = dict['first_name'] if 'first_name' in dict else ''
        self.last_name = dict['last_name'] if 'last_name' in dict else ''
        self.position = dict['position'] if 'position' in dict else ''
        self.hotel_id = int(dict['hid']) if 'hid' in dict else 0

    def __str__(self, *args, **kwargs):
        return self.first_name + ' ' + self.last_name

    def to_sql(self):
        return 'passport = %s, ' \
               'salary =  %s, ' \
               'first_name = "%s", ' \
               'second_name = "%s", ' \
               'position = "%s"' % (
                   self.passport,
                   self.salary,
                   self.first_name,
                   self.last_name,
                   self.position)


class Manager(Staff):
    def __init__(self, dict):
        if dict is None:
            dict = {}
        super(Manager, self).__init__(dict)
        self.id = dict['sid'] if 'sid' in dict else None
        self.login = dict['login'] if 'login' in dict else None
        self.password = dict['password'] if 'password' in dict else None


class Booking:
    def __init__(self, dict):
        if dict is None:
            dict = {}
        self.id = dict['id'] if 'id' in dict else None
        self.room_id = dict['rid'] if 'rid' in dict else None
        self.user_id = dict['uid'] if 'uid' in dict else None
        self.check_in_date = dict['check_in'] if 'check_in' in dict else None
        self.check_out_date = dict['check_out'] if 'check_out' in dict else None
        self.money = dict['money'] if 'money' in dict else None
        self.booking_date = dict['booking_date'] if 'booking_date' in dict else None
        self.status = int(dict['status']) if 'status' in dict else None


class Feedback:
    def __init__(self, dict):
        if dict is None:
            dict = {}
        self.id = dict['id'] if 'id' in dict else None
        self.hotel_id = dict['hid'] if 'hid' in dict else None
        self.text = dict['feedback'] if 'feedback' in dict else None
        self.rating = dict['rating'] if 'rating' in dict else None


class Hotel:
    def __init__(self, dict):
        if dict is None:
            dict = {}
        self.id = int(dict['id']) if 'id' in dict else None
        self.name = dict['name'] if 'name' in dict else None
        self.url = dict['url'] if 'url' in dict else None
        self.longitude = float(dict['longitude']) if 'longitude' in dict else None
        self.latitude = float(dict['latitude']) if 'latitude' in dict else None
        self.address = dict['address'] if 'address' in dict else None
        self.image_url = dict['image_url'] if 'image_url' in dict else 'http://www.zimaletta.com.ua/ufiles/hotels/photos/Titanik_013.jpg'
        self.city = dict['city'] if 'city' in dict else None
        self.stars = int(dict['stars']) if 'stars' in dict else None
        self.rating = dict['rating'] if 'rating' in dict else None
        self.budget = int(dict['budget']) if 'budget' in dict else None

        self.rooms = []


class Room:
    def __init__(self, dict):
        if dict is None:
            dict = {}
        self.id = dict['id'] if 'id' in dict else None
        self.hotel_id = dict['hid'] if 'hid' in dict else None
        self.room_category_id = dict['rcid'] if 'rcid' in dict else None
        self.price = dict['price'] if 'price' in dict else None
        self.room_number = dict['room_number'] if 'room_number' in dict else None
        self.image_url = dict['image_url'] if 'image_url' in dict else 'http://www.svoiludi.ru/images/tb/10625/al-raha-beach-hotel-1384335128738_w990h700.jpg'
        self.room_type = dict['type'] if 'type' in dict else None
        self.room_for_disabled = dict['for_disabled'] if 'for_disabled' in dict else None
        self.capacity = dict['max'] if 'max' in dict else None
        self.breakfast = dict['breakfast'] if 'breakfast' in dict else None
        self.parking = dict['parking'] if 'parking' in dict else None


class User:
    def __init__(self, dict):
        if dict is None:
            dict = {}
        self.id = dict['id'] if 'id' in dict else None
        self.first_name = dict['first_name'] if 'first_name' in dict else None
        self.last_name = dict['last_name'] if 'last_name' in dict else None
