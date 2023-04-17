import gkeepapi
from flask import abort
import json
import atexit

from . import config


def cached(func):
    cache = dict()

    def wrapper(self, key):
        if key not in cache:
            cache[key] = func(self, key)
        return cache[key]

    wrapper.__name__ = func.__name__
    return wrapper


class WrappedKeep(gkeepapi.Keep):
    def find_labels_extended(self, labels):
        print("searcg notes with labels:", labels)
        result = None
        if not labels:
            abort(400, "empty labels search")
        for label in labels:
            # plaintext search
            matched_1 = set([n.server_id for n in self.find("#" + label)])
            # TODO: avoid false-positive labels cause by prefix overlay

            # labels search
            genuine_label = self.findLabel(label)
            if genuine_label:
                notes = self.find(labels=[genuine_label])
                matched_2 = set([n.server_id for n in notes])
            else:
                matched_2 = set()
            matched = matched_1 | matched_2

            if result is None:
                result = matched
            else:
                result &= matched

        result = [self.get(id) for id in matched]
        return result


keep = WrappedKeep()


def init():
    try:
        with open(config.cache_path + "/keep.json", "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None

    try:
        print("trying to login by password")
        keep.login(config.keep_user, config.keep_pasw, state=state, sync=False)
    except gkeepapi.exception.LoginException:
        print("trying to login by master_token")
        keep.resume(
            config.keep_user,
            config.keep_master_token,
            state=state,
            sync=False,
        )


def save():
    with open("cache/keep.json", "w") as f:
        json.dump(keep.dump(), f)


atexit.register(save)
