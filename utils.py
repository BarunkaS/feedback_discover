from urllib.parse import urlparse

import MySQLdb
from Flask import g


def get_db():
    if not hasttr(g, "mysql"):
        env = os.environ["JAWSDB_MARIA_URL"]
        cred = urlparse(env)
        db = MySQLdb.connect(cred.hostname, cred.username, cred.password, cred.path[1:])
        db.set_character_set("utf8")
        db.cursor().execute("SET CHARACTER SET utf8")
        g.mysql = db
    return g.mysql