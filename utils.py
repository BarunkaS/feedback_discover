from urllib.parse import urlparse

import MySQLdb
from flask import g


def get_db():
    if not hasattr(g, "mysql"):
        env = os.environ["JAWSDB_MARIA_URL"]
        cred = urlparse(env)
        db = MySQLdb.connect(cred.hostname, cred.username, cred.password, cred.path[1:])
        db.set_character_set("utf8")
        db.cursor().execute("SET CHARACTER SET utf8")
        g.mysql = db
    return g.mysql