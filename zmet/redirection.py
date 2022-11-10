"""
#rd <key>
<url>
<search> or ""
"""

from flask import redirect
from .keep import keep


def try_redirect(query):
    print("try_redirecting", query)
    if not query:
        return None
    words = query.split(" ")
    note = keep.find_redirection(words[0])
    if not note:
        print("try_redirecting", "no red")
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
