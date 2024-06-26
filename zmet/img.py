from flask import Blueprint, abort, send_file
from flask_login import login_required
from .keep import keep
import os
import requests
import shutil
from . import config
from . import access

img = Blueprint("img", __name__, url_prefix="/img")
IMG_CACHE_PATH = config.cache_path + "/img"


@img.route("/<id>")
def get(id):
    try:
        note_id, index = id.split(":")
    except ValueError:
        abort(400, description="invalid id")
    note = keep.get(note_id)
    if not note:
        abort(404, "note not found")
    if access.access_to(note) < access.VIEW:
        abort(403)
    filename = f"{IMG_CACHE_PATH}/{id}"
    if id not in os.listdir(IMG_CACHE_PATH):
        if note is None:
            abort(404, description="image parent not found")
        try:
            blob = note.images[int(index)]
        except IndexError:
            abort(404, description="index out of range")
        except ValueError:
            abort(400, description="invalid index")
        url = keep.getMediaLink(blob)
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            abort(response.status_code, description="image cannot be fetched")
        with open(filename, "wb") as file:
            shutil.copyfileobj(response.raw, file)

    return send_file(filename, mimetype='image/gif')
