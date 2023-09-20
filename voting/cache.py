import sqlite3
from flask_caching import Cache
from flask import Flask, current_app, g
from voting.db import get_db


cache = Cache()

def get_cache() -> Cache:
    return cache

def init_cache(app: Flask):
    cache.init_app(app)


def get_classes_from_database() -> list:
    """Retrieves all the classes that take part in the vote. \n
    Returns a list of tuples, where each tuple contains just one 'String'
    """
    # FIXME: seems like flask caching does not work with returning 'sqlite3.Row' objects
    # db = get_db()
    # classes = db.execute('SELECT DISTINCT class FROM user',).fetchall()
    # print(classes[0][0])
    # return classes

    con = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    cursor = con.cursor()
    res = cursor.execute('SELECT DISTINCT class FROM user',).fetchall()
    print(type(res))
    print(res)
    con.close()
    return res

@cache.cached(key_prefix='classes')
def get_cached_classes():
    return get_classes_from_database()
