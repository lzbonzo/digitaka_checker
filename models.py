from pony.orm import Database, Required

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    host='127.0.0.1', # warning: choose your localhost IP
    database='digitaka_urls')

db = Database()
db.bind(**DB_CONFIG)


class DigitakaUrls(db.Entity):
    """Url"""
    user_id = Required(int, unique=False)
    url = Required(str, unique=True)


db.generate_mapping(create_tables=True)
