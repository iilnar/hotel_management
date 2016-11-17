import datetime

months = ['emp', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
days = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def parse_month(msg: str):
    msg = msg.lower()
    if msg.isdigit():
        return int(msg)
    try:
        return months.index(msg)
    except ValueError:
        return 0


def parse_date(msg: str):
    return datetime.date(int(msg[0:4]), int(msg[5:7]), int(msg[8:]))


def dict_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('%s - %s' % (key, value))

    return "\n".join(facts).join(['\n', '\n'])


def unshared_copy(inList):
    if isinstance(inList, list):
        return list(map(unshared_copy, inList))
    return inList


class Room:
    def __init__(self, id: int, type: str, price: int, img: str):
        self.id = id
        self.type = type
        self.price = price
        self.img = img


class Hotel:
    def __init__(self, id: int, name: str, stars: int, url: str, img: str):
        self.id = id
        self.name = name
        self.address = None
        self.url = url
        self.img = img
        self.stars = stars
        self.rooms = []

    def add_room(self, room: Room):
        self.rooms.append(room)


hotel1 = Hotel(1, "Ildar hotel", 5, "http://vk.com/ildar", "https://pp.vk.me/c614731/v614731468/ad51/9h6mFWxP94Y.jpg")
hotel2 = Hotel(2, "Azat hotel", 3, "http://vk.com/ildar", "https://pp.vk.me/c419930/v419930468/568d/wbrhwV1h_BI.jpg")
hotel3 = Hotel(3, "Aydarbek hotel", 4, "http://vk.com/ildar", "https://pp.vk.me/c419930/v419930468/5683/d_yTL9UE2Vo.jpg")

room1 = Room(1, "Single", 100, "https://pp.vk.me/c419930/v419930468/5683/d_yTL9UE2Vo.jpg")
room2 = Room(2, "Twin", 150, "https://pp.vk.me/c419930/v419930468/568d/wbrhwV1h_BI.jpg")
room3 = Room(3, "Type", 300, "https://pp.vk.me/c10613/u1704468/122504714/w_50687b0b.jpg")
room4 = Room(4, "sa", 12, "https://pp.vk.me/c10181/u1704468/132060492/y_f3631361.jpg")
room5 = Room(5, "sad", 141, "https://pp.vk.me/c10344/u1704468/137115752/y_64defdb7.jpg")
room6 = Room(6, "asda", 3214, "https://pp.vk.me/c10036/u1704468/120489006/z_17504ee6.jpg")

hotel1.add_room(room1)
hotel1.add_room(room2)
hotel1.add_room(room6)

hotel2.add_room(room3)
hotel2.add_room(room4)
hotel2.add_room(room5)

hotel3.add_room(room2)
hotel3.add_room(room1)
hotel3.add_room(room5)

hotels = [hotel1, hotel2, hotel3]