import sqlite3
from flask import g


class Database():
    def __init__(self, path):
        self.path = path
        self.db = self.get_db()

    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.path, isolation_level=None)
            db.row_factory = self.dict_factory
        return db

    # dict_factory
    # Converts the given _row_ from the to a dictionary

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # query
    # Once created, queries the database with _query_

    def query_db(self, query, args=(), one=False):
        cur = self.db.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    # clear
    # Removes all entries from _table_

    def clear(self, table):
        self.db.execute('DELETE FROM '+table)
