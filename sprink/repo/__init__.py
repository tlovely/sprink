import aiosqlite
import time
import json
import os

from sprink.config import DB_PATH

_cache = {}


def connect(commit = False, cache = False):
    assert not (commit and cache)
    def _connect(fn):
        async def _connected(*args, **kwargs):
            cache_key = (
                fn, 
                args[1:] if args and isinstance(args[0], aiosqlite.core.Connection) else args, 
                tuple(kwargs.items())
            )
            if cache and cache_key in _cache and _cache[cache_key]['mtime'] == os.stat(DB_PATH).st_mtime:
                return _cache[cache_key]['result']

            if commit:
                _cache.clear()

            if args and isinstance(args[0], aiosqlite.core.Connection):
                result = await fn(*args, **kwargs)
            else:
                async with aiosqlite.connect(DB_PATH) as con:
                    con.row_factory = aiosqlite.Row
                    result = await fn(con, *args, **kwargs)
                    if commit:
                        await con.commit()
            
            if cache:
                _cache[cache_key] = {'mtime': os.stat(DB_PATH).st_mtime, 'result': result}

            return result
        return _connected
    # if bool, connect is being called before decoration
    return _connect if isinstance(commit, bool) else _connect(commit)


def now():
    return int(time.time() * 1000)


with open('.zones.json') as out:
    ZONES = {int(key): value for key, value in json.load(out).items()}