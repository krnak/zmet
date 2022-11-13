"""
#label <name>
#<label_1> #<label_2> ...
"""

from .keep import keep
from gkeepapi.node import Note

CACHE = dict()


def labels_of(x):
    if isinstance(x, str):
        note = CACHE.get(x)
        if not note:
            return None
        lines = note.text.split("\n")
        if not lines:
            return []
        labels = lines[-1].split(" ")
        return set(x[1:] for x in labels if x[0] == "#")
    elif isinstance(x, Note):
        labels = set(label.name for label in x.labels)
        for line in [x.title] + x.text.split("\n"):
            for word in line.split(" "):
                if word.startswith("#"):
                    labels.add(word[1:])
        return labels


def is_public(note):
    return "public" in labels_of(note)


def sync():
    global CACHE
    CACHE = dict()
    labels = keep.find(labels=[keep.findLabel("label")])
    for label in labels:
        key = label.title[7:]
        CACHE[key] = label
