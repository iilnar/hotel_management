class Staff:
    def __init__(self, dict):
        self.passport = dict['passport']
        self.salary = dict['salary']
        self.first_name = dict['first_name']
        self.second_name = dict['second_name']
        self.position = dict['position']
        self.hotel_id = dict['hid']

    def __str__(self, *args, **kwargs):
        return self.first_name + ' ' + self.second_name


class Manager(Staff):
    def __init__(self, dict):
        super(Manager, self).__init__(dict)
        self.id = dict['sid']
        self.login = dict['login']
        self.password = dict['password']


class Booking:
    def __init__(self, dict):
        self.id = dict['id']
        self.room_id = dict['rid']
        self.user_id = dict['uid']
        self.check_in_date = dict['check-in']
        self.check_out_date = dict['check-out']
        self.money = dict['money']
        self.booking_date = dict['booking_date']


class Feedback:
    def __init__(self, dict):
        self.id = dict['id']
        self.hotel_id = dict['hid']
        self.text = dict['feedback']
        self.rating = dict['rating']


class Hotel:
    def __init__(self, dict):
        self.id = dict['id']
        self.name = dict['name']
        self.url = dict['url']
        self.longitude = dict['longitude']
        self.latitude = dict['latitude']
        self.address = dict['address']
        self.image_url = dict['image']
        self.city = dict['city']
        self.start = dict['stars']
        self.rating = dict['rating']
        self.budged = dict['budget']


class Room:
    def __init__(self, dict):
        self.id = dict['id']
        self.hotel_id = dict['hid']
        self.room_category_id = dict['rcid']
        self.price = dict['price']
        self.room_number = dict['room_number']

        self.room_type = dict['type']
        self.room_for_disabled = dict['for_disable']
        self.capacity = dict['max']
        self.breakfast = dict['breakfast']
        self.parking = dict['parking']


class User:
    def __init__(self, dict):
        self.id = dict['id']
        self.first_name = dict['name']
        self.second_name = dict['surname']
