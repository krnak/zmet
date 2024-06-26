from flask import Blueprint, render_template, abort, request
from flask_login import current_user, login_required
import markdown

from .keep import keep
from .label import is_public, labels_of
from .access import visible
from .ordering import order

wall_bp = Blueprint("wall", __name__, template_folder='templates')


class Card:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def note_to_card(note):
    # add thumbnail
    thumbnail = f"/img/{note.server_id}:0" if note.images else None

    # strip labels
    lines = note.text.split("\n")
    while lines and lines[-1] == "":  # strip empty lines
        lines.pop()
    if lines and lines[-1].startswith("#"):
        lines = lines[:-1]
    text = "\n".join(lines)

    html: str = ""
    if keep.findLabel("bm") in note.labels.all():
        link = note.text.split("\n")[0]
    else:
        link = "/note/" + note.server_id
        if "dontstrip" in labels_of(note) or len(text) < 300:
            md = markdown.Markdown(extensions=["nl2br"])
            html = md.convert(text)
        else:
            html = "".join(
                f"<p>{line}</p>"
                for line in (text[:297] + "...").split("\n")
            )


    return Card(
        thumbnail=thumbnail,
        title=note.title,
        text=html,
        link=link,
    )


@wall_bp.route("/wall")
def wall():
    labels = request.args.get("labels")
    query = request.args.get("q")
    if (labels and query) or (not labels and not query):
        abort(404, "invalid number of arguments")

    if labels:
        notes = keep.find_labels_extended(labels.split(","))
    else:
        if current_user.id != "admin":
            abort(403, "only label view allowed for anonymous users")
        notes = keep.find(query)

    notes = list(visible(notes))
    notes.sort(key=lambda x: x.timestamps.created, reverse=True)
    notes = order(notes)

    if not notes:
        return "<h1>empty wall</h1>"

    return render_template(
        "wall.html",
        cards=[note_to_card(note) for note in notes],
        title="Změť - " + (labels or query),
    )
