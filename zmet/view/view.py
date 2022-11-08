from flask import Blueprint, render_template, abort
import markdown

from ..keep import keep

view = Blueprint("view", __name__, template_folder='templates')


class Card:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def get_thumbnail(note):
    if note.images:
        return f"/img/{note.server_id}:0"
    else:
        return None


@view.route("/wall/<label>")
def wall(label):
    if label not in ["blog", "test"]:
        abort(403)
    cards = [
        Card(
            thumbnail=get_thumbnail(note),
            title=note.title,
            text=markdown.markdown(note.text, extensions=['nl2br']),
        )
        for note in keep.find(labels=[keep.findLabel(label)])
    ]
    return render_template(
        "wall.html",
        cards=cards,
        title="Změť: blog",
    )
