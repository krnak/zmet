from flask import Blueprint, render_template, abort, request
from flask_login import current_user
import markdown

from ..keep import keep

view = Blueprint("view", __name__, template_folder='templates')


class Card:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def note_to_card(note):
    if note.images:
        thumbnail = f"/img/{note.server_id}:0"
    else:
        thumbnail = None

    # remove last line if i contains labels
    lines = note.text.split("\n")
    if lines:
        if "#" in lines[-1]:
            lines = lines[:-1]
    text = "\n".join(lines)

    md = markdown.Markdown(extensions=["nl2br", "meta"])
    html = md.convert(text)
    link = md.Meta.get("link", [None])[0]

    return Card(
        thumbnail=thumbnail,
        title=note.title,
        text=html,
        link=link,
    )


@view.route("/wall")
def wall():
    label = request.args.get("label")
    if not label:
        abort(404, "label argument required")

    if label not in ["blog", "test"]:
        if current_user.is_anonymous:
            abort(403)

    notes = keep.find_labels_extended([label])
    notes.sort(key=lambda x: x.timestamps.updated)
    return render_template(
        "wall.html",
        cards=[note_to_card(note) for note in notes],
        title="Změť: " + label,
    )
