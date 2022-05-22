import asyncio
import json

from sprink.repo import user

loop = asyncio.get_event_loop()

username = input('username: ')
password = input('password: ')

user = loop.run_until_complete(user.create(username, password))

print(f'user_id:  {user["id"]}')