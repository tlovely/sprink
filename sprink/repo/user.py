from uuid import uuid4
from hashlib import sha256

from sprink.repo import connect


def _hash(password):
    return sha256(password.encode()).hexdigest()


@connect(cache=True)
async def get(con, user_id = None, token = None):
    if user_id is not None:
        query = (
            'select * from user where id = ?;'
            if isinstance(user_id, int) else
            'select * from user where username = ?;'
        )
        cur = await con.execute(query, (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None
    elif token is not None:
        cur = await con.execute(
            'select * from user where token = ?;',
            (token,)
        )
        row = await cur.fetchone()
        return dict(row) if row else None
    else:
        cur = await con.execute('select id, username from user;')
        return await [dict(row) for row in cur.fetchall()]


@connect(commit=True)
async def create(con, username, password):
    await con.execute(
        'insert into user ( username, password_hash ) values ( ?, ? );',
        # Not the best approach for hashing passwords, but doesn't matter
        # in this application.
        (username, _hash(password))
    )
    return await get(con, username)


@connect(commit=True)
async def validate(con, user_id, password):
    user = await get(con, user_id)
    if user['password_hash'] == _hash(password):
        if user['token']:
            return user['token']
        else:
            token = uuid4().hex
            await con.execute('update user set token = ? where id = ?;', (token, user['id']))
            return token


@connect(commit=True)
async def update_password(con, user_id, password, password_new):
    user_ = await get(con, user_id)
    if await validate(con, user_id, password):
        await con.execute(
            'update user set password_hash = ?, token = null where id = ?;', 
            (_hash(password_new), user_['id'])
        )
        return True
    return False


