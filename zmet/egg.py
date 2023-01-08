from flask import Blueprint, abort
from .keep import keep
from . import config
import time

egg_bp = Blueprint("egg", __name__, url_prefix="/egg")

@egg_bp.route("/<id>")
def get(id):
    eggs = list(keep.find(f"#egg { id }", labels=[keep.findLabel("egg")]))
    if not eggs:
        abort(404)
    egg = eggs[0]
    egg.text += f"viewed { time.strftime("%Y-%m-%d %H:%M:%S") } { int(time.time()) }\n"
    return f"Congrats! You found egg { id }. For more info contact me at { config.keep_user }."
