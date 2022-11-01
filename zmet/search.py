from flask import (
    request,
    flash,
    redirect,
    Blueprint,
)
from flask_login import login_required
from .keep import keep

search = Blueprint("search", __name__, url_prefix="/search")


@search.route("/")
@login_required
def index():
    query = request.args.get("q")
    if query:
        redirection = find_redirection(query)
        if redirection:
            return redirection
        if query.startswith("s "):
            return find_notes(query[2:])
        if query.startswith("#"):
            return find_notes(query)
        return redirect("https://google.com/search?q=" + query)
    else:
        return """
        <form action="/search" method="GET">
            <input type="text" name="q">
            <button>search</button>
        </form>
        """


def find_notes(query):
    labels = []
    words = []
    for word in query.split("."):
        if word.startswith("#"):
            label = keep.findLabel(word[1:])
            if label:
                labels.append(label)
            else:
                flash(f"unknow label {word}")
        else:
            words.append(word)
    res = "<ul>"
    for note in keep.find(query=" ".join(words), labels=labels):
        name = note.title if note.title else note.server_id
        res += f"<li><a href='/s/{note.server_id}'>{name}</li>"
    res += "</ul>"
    return res


def find_redirection(query):
    words = query.split(" ")
    keyword = words[0]
    redirection = list(keep.find(
        "#rd " + keyword,
        labels=[keep.findLabel("rd")],
    ))
    if len(redirection) > 2:
        return "more redirection found"
    if redirection:
        site, search, *_ = redirection[0].text.split("\n")
        query = " ".join(words[1:])
        if query:
            link = search.format(query=query)
        else:
            link = site
        return redirect(link)
    else:
        return None
