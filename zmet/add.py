from flask import redirect, request, Blueprint
from flask_login import login_required
from flask_wtf.csrf import generate_csrf
from .keep import keep

add = Blueprint("add", __name__, url_prefix="/add")


@add.route("/note", methods=["GET"])
@login_required
def add_note_get():
    return f"""
    <h3 class="title">create note</h3></ br>
    <form method="POST" action="/add/note">
        <input type="text" name="title"></ br>
        <textarea name="text" rows="5" cols="33"></textarea></ br>
        <input type="text" name="labels"></ br>
        <input type="hidden" name="csrf_token" value="{ generate_csrf() }" />
        <button>create</button>
    </form>
    """


@add.route("/note", methods=["POST"])
@login_required
def add_note_post():
    title = request.form.get("title") or ""
    text = request.form.get("text") or ""
    labels = request.form.get("labels") or ""
    note = add_note_inner(title, text, labels)
    return redirect("/s/" + note.server_id)


def add_note_inner(title="", text="", labels=""):
    note = keep.createNote(title, text)
    for label_name in labels.split(","):
        label = keep.findLabel(label_name, create=True)
        note.labels.add(label)
    keep.sync()
    return note


@add.route("/bookmark", methods=["POST"])
@login_required
def add_bookmark_inner():
    pass


@add.route("/redirection", methods=["POST"])
@login_required
def add_redirection_inner():
    pass
