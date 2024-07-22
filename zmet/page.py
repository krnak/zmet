from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from .keep import keep
from .label import is_public
from . import access
import markdown

page = Blueprint("page", __name__)


@page.route("/note/<id>")
def note(id):
    note = keep.get(id)
    if not note:
        abort(404, "note not found")
    if access.access_to(note) < access.VIEW:
        abort(403)
    content = []
    # TODO: move content creation into jinja
    if note.images:
        content.append(f'<img src="/img/{ note.server_id }:0" /><br />')
    if note.title:
        content.append(f"<h1>{ note.title }</h1><br />")

    # strip labels and short links
    lines = note.text.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[-1].startswith("#"):
        lines.pop()
    while lines and lines[-1].startswith("shortlink: "):
        lines.pop()
    text = "\n".join(lines)

    if text:
        content.append(markdown.markdown(text, extensions=[
            "nl2br",
            "fenced_code",
            "mdx_linkify", # makes links clickable with `linkify` extension
        ]))

    return render_template("page.html", content="".join(content))
