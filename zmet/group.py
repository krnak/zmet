from flask import abort
from .keep import keep
from .label import is_public

CACHE = dict()

class Group:
    def __init__(self, note):
        self.name = note.title[len("#group "):]
        salt_note = list(keep.find(f"#groupsaltfor { self.name }"))
        self.salt = salt_note[0].text if salt_note else ""
        self.users = note.text.split("\n")
        self.note = note

    def add_member(self, name):
        if name not in self.users:
            self.users.append(name)
            self.note.text += "\n" + name
            keep.sync()

    def verify_salt(self, salt):
        if salt != self.salt:
            abort(403, "invalid link")


def sync():
    global CACHE
    CACHE = dict()
    group_notes = keep.find(labels=[keep.findLabel("group")])
    for group_note in group_notes:
        group = Group(group_note)
        CACHE[group.name] = group


def get_groups_of(note):
    groups = dict()
    for word in note.text.split():
        if len(word) >= 2 and word[0] == "^" and word[1] != "@":
            group_name = word[1:]
            if group_name in CACHE:
                groups[group_name] = CACHE[group_name]
    return groups


def get_groups():
    return CACHE


def get_link_groups():
    groups = list(keep.find(
        "#zmet group links",
        labels=[keep.findLabel("zmet")]
    ))[0].text.split()
    return {x: CACHE.get(x) for x in groups if x in CACHE}
