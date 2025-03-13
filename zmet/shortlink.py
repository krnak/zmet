from flask import Blueprint, abort, redirect, url_for
from .keep import keep
from .auth import admin_required
from . import page
from . import crypto

shortlink_bp = Blueprint("shortlink", __name__, url_prefix="/s")


@shortlink_bp.route("/<name>")
def shortlink(name):
    notes = list(keep.find("shortlink: " + name))
    if not notes:
        abort(404)
    else:
        return page.note(id=notes[0].id)

@shortlink_bp.route("/<name>/meta")
@admin_required
def shortlink_vt(name):
    notes = list(keep.find("shortlink: " + name))
    if not notes:
        abort(404)
    note = notes[0]

    meta = {
        "view_token": "vt=" + crypto.node_view_token(note),
    }

    return "<br />".join([k + ": " + v for k, v in meta.items()])
