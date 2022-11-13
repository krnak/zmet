"""
#rd <key>
<url>
<search> or ""
"""

from flask import redirect
from .keep import keep

CACHE = dict()


def try_redirect(query):
    if not query:
        return None
    words = query.split(" ")
    note = CACHE.get(words[0])
    if not note:
        return None
    lines = note.text.split("\n")
    url = lines[0]
    if len(lines) > 1:
        search = lines[1]
    else:
        search = ""

    if words[1:]:
        if not search:
            return None
        query = " ".join(words[1:])
        return redirect(search.format(query=query))
    else:
        return redirect(url)


def sync():
    global CACHE
    CACHE = dict()
    rds = keep.find(labels=[keep.findLabel("rd")])
    for rd in rds:
        key = rd.title[4:]
        CACHE[key] = rd
