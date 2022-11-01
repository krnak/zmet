from flask import Blueprint
from flask_login import login_required
from .keep import keep
import markdown

links = Blueprint("links", __name__, url_prefix="/s")


@links.route("/<id>")
@login_required
def link(id):
    note = keep.get(id)
    if note:
        labels = [
            f'<a href="/search?q=%23{label.name}">#{label.name}</a>'
            for label in note.labels.all()
        ]
        return f"""
        <div class="note">
            <h3>{note.title}</h3>
            {markdown.markdown(note.text)}
            {", ".join(labels)}
        </div>
        """
    else:
        return "not found"
