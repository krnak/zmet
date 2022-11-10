from gkeepapi import Keep
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


class WrappedKeep(Keep):
    def find_labels_extended(self, labels):
        print("seatch", labels)
        result = None
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

        result = [self.get(id) for id in result]
        return result

    @cached
    def find_redirection(self, key):
        notes = list(filter(
            lambda x: x.title == f"#rd {key}",  # avoid prefix collisions
            keep.find(
                f"#rd {key}",
                labels=[keep.findLabel("rd")]
            )
        ))
        if not notes:
            return None
        if len(notes) > 1:
            abort(500, f"two or more redirections found for key {key}")
        return notes[0]

    @cached
    def find_label_note(self, key):
        notes = list(filter(
            lambda x: x.title == f"#label {key}",  # avoid prefix collisions
            keep.find(
                f"#label {key}",
                labels=[keep.findLabel("label")]
            )
        ))
        if not notes:
            return None
        if len(notes) > 1:
            abort(500, f"two or more labels found for key {key}")
        return notes[0]


keep = WrappedKeep()


def init():
    try:
        with open("cache/keep.json", "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        state = None

    keep.login(config.keep_user, config.keep_pasw, state=state, sync=False)


def save():
    with open("cache/keep.json", "w") as f:
        json.dump(keep.dump(), f)


atexit.register(save)
