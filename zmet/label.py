"""
#label <name>
#<label_1> #<label_2> ...
"""

from .keep import keep
from gkeepapi.node import Note, List

CACHE = dict()


class Label:
    def __init__(self, note):
        self.note = note
        self.name = note.title[len("#label "):]
        #self.salt = ""
        #for line in note.text.split("\n"):
        #    if line.startswith("salt: "):
        #       self.salt = line[len("salt: "):]
        self.labels = labels_of(note)


def labels_of(x):
    if isinstance(x, str):
        note = CACHE.get(x)
        if not note:
            return []
        words = note.text.split()
        return set(x[1:] for x in words if x.startswith("#"))
    elif type(x) in (Note, List):
        keep_labels = set(label.name for label in x.labels.all())
        text_labels = set(x[1:] for x in x.text.split() if x.startswith("#"))
        return keep_labels | text_labels
    else:
        raise ValueError(f"invalid class: { type(x) }")


def is_public(note):
    for label in labels_of(note):
        # directly labeled as public
        if label == "public":
            return True
        # transitive publicity
        if label in CACHE and "public" in CACHE[label].labels:
            return True
    return False


def sync():
    global CACHE
    CACHE = dict()
    labels = keep.find(labels=[keep.findLabel("label")])
    for label_note in labels:
        label = Label(label_note)
        CACHE[label.name] = label


def get_labels():
    return CACHE
