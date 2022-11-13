from flask import Blueprint, render_template, abort, request
from flask_login import current_user
import markdown

from .keep import keep
from .label import is_public

wall_bp = Blueprint("wall", __name__, template_folder='templates')


class Card:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def note_to_card(note):
    if note.images:
        thumbnail = f"/img/{note.server_id}:0"
    else:
        thumbnail = None

    lines = note.text.split("\n")
    if lines and lines[-1] and lines[-1][0] == "#":
        lines[-1] = " " + lines[-1]
    text = "\n".join(lines)

    md = markdown.Markdown(extensions=["nl2br"])
    html = md.convert(text)
    # TODO: click-able cards
    # TODO: card teaser
    if keep.findLabel("bm") in note.labels.all():
        link = note.text.split("\n")[0]
        html = ""
    else:
        link = None

    return Card(
        thumbnail=thumbnail,
        title=note.title,
        text=html,
        link=link,
    )


@wall_bp.route("/wall")
def wall():
    label = request.args.get("label")
    query = request.args.get("q")
    if (label and query) or (not label and not query):
        abort(404, "invalid number of arguments")

    if label:
        notes = keep.find_labels_extended([label])
    else:
        if current_user.is_anonymous:
            abort(403, "only label view allowed for anonymous users")
        notes = keep.find(query)

    if current_user.is_anonymous:
        notes = filter(is_public, notes)

    notes = list(notes)
    notes.sort(key=lambda x: x.timestamps.updated)

    if not notes:
        return "<h1>empty wall</h1>"

    return render_template(
        "wall.html",
        cards=[note_to_card(note) for note in notes],
        title="Změť - " + (label or query),
    )
