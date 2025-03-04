from flask import Blueprint, abort, redirect, url_for
from .keep import keep
from . import page

shortlink_bp = Blueprint("shortlink", __name__, url_prefix="/s")


@shortlink_bp.route("/<name>")
def shortlink(name):
    notes = list(keep.find("shortlink: " + name))
    if not notes:
        abort(404)
    else:
        return page.note(id=notes[0].id)
