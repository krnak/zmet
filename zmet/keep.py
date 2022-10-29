from gkeepapi import Keep
import json
import atexit

from . import config

keep = Keep()


def init():
    try:
        with open("cache/keep.json", "r") as f:
            state = json.load(f)
            keep.restore(state)
            print("keep restored")
    except FileNotFoundError:
        pass

    keep.login(config.keep_user, config.keep_pasw)


def outit():
    with open("cache/keep.json", "w") as f:
        json.dump(keep.dump(), f)


atexit.register(outit)
