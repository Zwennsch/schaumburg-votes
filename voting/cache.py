import sqlite3
from flask_caching import Cache
from flask import Flask, current_app
# from voting.db import get_dbn 


cache = Cache()

def get_cache() -> Cache:
    return cache

def init_cache(app: Flask):
    cache.init_app(app)


def _get_classes_from_database() -> list:
    """Retrieves all the classes that take part in the vote. \n
    Returns a list of tuples, where each tuple contains just one 'String'
    """
    # Using the cursor instead of get_db() since Flask caching does not work with 
    # sqlite3.Row since Row objects are not picklable 
    con = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    cursor = con.cursor()
    res = cursor.execute('SELECT DISTINCT class FROM user',).fetchall()
    con.close()
    return res

@cache.cached(key_prefix='classes')
def get_cached_classes():
    return _get_classes_from_database()
