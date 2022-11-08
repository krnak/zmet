from gkeepapi import Keep
import json
import atexit

from . import config


class WrappedKeep(Keep):
    def find_labels_extended(self, labels):
        result = None
        for label in labels:
            # plaintext search
            matched = set([n.server_id for n in self.find("#" + label)])
            # TODO: avoid false-positive labels cause by prefix overlay

            # labels search
            genuine_label = self.findLabel(label)
            if genuine_label:
                notes = self.find(labels=[genuine_label])
                matched |= set([n.server_id for n in notes])

            if result is None:
                result = matched
            else:
                result &= matched

        result = [self.get(id) for id in result]
        return result


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
