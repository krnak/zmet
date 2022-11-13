from flask import redirect, request, Blueprint, abort, url_for, render_template
from flask_login import login_required
from flask_wtf.csrf import generate_csrf
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from .keep import keep
from .auth import admin_required

add = Blueprint("add", __name__, url_prefix="/add", template_folder="templates")


@add.route("/note", methods=["GET"])
@admin_required
def note_form():
    return render_template(
        "add_note.html",
        args=request.args,
        csfr_token=generate_csrf(),
    )


@add.route("/note", methods=["POST"])
@admin_required
def note():
    title = request.form.get("title") or ""
    text = request.form.get("text") or ""
    labels = request.form.get("labels") or ""
    note = add_note_inner(title, text, labels)
    next = request.form.get("next", f"/s/{note.server_id}")
    return redirect(next)


def add_note_inner(title="", text="", labels=""):
    print("creating new note:", title)
    note = keep.createNote(title, text.replace("\r", ""))
    for label_name in labels.split(","):
        label = keep.findLabel(label_name)
        if label:
            note.labels.add(label)
    keep.sync()
    print("new note id:", note.server_id)
    return note


@add.route("/bookmark", methods=["GET"])
@admin_required
def bookmark():
    query = request.args.get("q")
    if not query:
        abort(404, "q argument is missing")
    words = query.split(" ")
    if len(words) < 2:
        abort(404, "too few words")
    label = words[0]
    url = words[-1]
    title = " ".join(words[1:-1])
    if not title:
        try:
            title = get_page_title(url)
        except:
            title = "no title"
    labels = ["bm"]
    if keep.findLabel(label):
        labels.append(label)
    return redirect(url_for(
        "add.note",
        title=quote_plus(title),
        text=quote_plus(f"{ url }\n#{ label }"),
        labels=",".join(labels),
        next=quote_plus(url)
    ))


@add.route("/redirection", methods=["GET"])
@admin_required
def redirection():
    query = request.args.get("q")
    if not query:
        abort(404, "q argument is missing")
    words = query.split(" ")
    if len(words) < 2:
        abort(404, "too few words")
    key = words[0]
    url = words[1]
    if len(words) > 2:
        search = words[2]
    else:
        search = ""
    return redirect(url_for(
        "add.note",
        title=quote_plus(f"#rd {key}"),
        text=quote_plus(f"{url}\n{search}"),
        labels="rd",
        next=quote_plus(url),
    ))


def get_page_title(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text)
    return soup.title.string
