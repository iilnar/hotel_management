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
