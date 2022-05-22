import sqlite3

from os.path import exists
from glob import glob

from sprink.config import DB_PATH

PREFIX = '[1234567890]' * 3

migrations = glob(f'migrations/{PREFIX}_*.sql')
current = None

if exists(DB_PATH):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute('select current from migrations;')
        current = cur.fetchone()[0]

run = current is None
with sqlite3.connect(DB_PATH) as con:
    for migration in migrations:
        if run:
            cur = con.cursor()
            print(f'executing: {migration}')
            with open(migration) as out:
                cur.executescript(out.read())
            current = migration[11:14]
            name = migration[15:-4]
            cur.execute('update migrations set current = ?, name = ?;', (current, name))
            con.commit()
        else:
            print(f'skipping: {migration}')

        run = migration.startswith(f'migrations/{current}_')