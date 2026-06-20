import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'smart_classroom_system',
    'user': 'postgres',
    'password': '123'
}


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(**DATABASE_CONFIG)
    return g.db


def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    db = get_db()
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params or ())
        if commit:
            db.commit()
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = psycopg2.connect(**DATABASE_CONFIG)
    with db.cursor() as cur:
        cur.execute(open('schema.sql', 'r', encoding='utf-8').read())
        db.commit()
    db.close()


if __name__ == '__main__':
    init_db()
    print('Database initialized.')
