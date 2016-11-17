import MySQLdb
from MySQLdb.cursors import DictCursor

import models


class DB:
    def __init__(self):
        self.db = MySQLdb.connect(host='localhost', user='root', passwd='password', db='hoteldb')

    def query(self, query, one=False):
        c = self.db.cursor(cursorclass=DictCursor)
        c.execute(query)
        res = c.fetchall()
        return (res[0] if res else None) if one else res

    def get_manager(self, login: str = None, id: int = None):
        if login is not None:
            return models.Manager(self.query('SELECT * FROM manager JOIN staff WHERE login = "%s"' % login, one=True))
        elif id is not None:
            return models.Manager(self.query('SELECT * FROM manager JOIN staff WHERE sid = "%s"' % id, one=True))

    def get_all_staff(self):
        return [models.Staff(x) for x in self.query("SELECT * FROM staff")]

    def get_staff(self, id: int):
        return models.Staff(self.query("SELECT * from staff WHERE passport = %s" % id, one=True))
