import random
from typing import Generator

from aiohttp.web_request import Request

animals = ['turtle', 'squirrel', 'bat']
colors = ['green', 'blue', 'orange']

usernames = [f"{color} {animal}" for color in colors for animal in animals]
random.shuffle(usernames)


def generate_usernames() -> Generator:
    for username in usernames:
        yield username


username_generator = generate_usernames()


def get_username(request: Request) -> str:
    """
    Assign a username to a request if it has none.
    """
    username = request.get('USERNAME')
    if username is None:
        username = next(username_generator)
        request['USERNAME'] = username
    return username, request
