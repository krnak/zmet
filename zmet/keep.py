from gkeepapi import Keep
import json
import atexit

from . import config

keep = Keep()


def init():
    try:
        with open("cache/keep.json", "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None

    keep.login(config.keep_user, config.keep_pasw, state=state, sync=False)


def outit():
    with open("cache/keep.json", "w") as f:
        json.dump(keep.dump(), f)


atexit.register(outit)
