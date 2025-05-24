from flask import Flask, redirect, url_for, render_template, request, abort

from flask_wtf.csrf import CSRFProtect
from urllib.parse import quote_plus, unquote_plus
from flask_login import login_required
import threading
import gkeepapi

from base64 import (
    urlsafe_b64encode as b64_encode,
    urlsafe_b64decode as b64_decode,
)
from . import saltpack_armor

from . import keep
from . import auth
from . import search
from . import page
from . import config
from . import add
from . import img
from . import wall
from . import redirection
from . import label
from . import egg
from . import group
from . import graph_api
from . import scripts
from . import shortlink

keep.init()

app = Flask("zmet", template_folder="templates")
app.secret_key = config.app_secret_key
app.debug = True
app.jinja_env.filters['quote_plus'] = lambda u: quote_plus(u)
app.jinja_env.filters['unquote_plus'] = lambda u: unquote_plus(u)

csrf = CSRFProtect()
csrf.init_app(app)

app.register_blueprint(auth.auth)
auth.init(app)
app.logger.info("auth registered")

app.register_blueprint(search.search)
app.logger.info("search registered")

app.register_blueprint(page.page)
app.logger.info("page registered")

app.register_blueprint(add.add)
app.logger.info("add registered")

app.register_blueprint(img.img)
app.logger.info("img registered")

app.register_blueprint(wall.wall_bp)
app.logger.info("wall registered")

app.register_blueprint(egg.egg_bp)
app.logger.info("egg registered")

app.register_blueprint(graph_api.graph_bp)
app.logger.info("graph_api registered")

app.register_blueprint(scripts.scripts_bp)
app.logger.info("scripts registered")

app.register_blueprint(shortlink.shortlink_bp)
app.logger.info("shortlink registered")

app.logger.info("running script scheduler")
threading.Thread(target=scripts.scripts_scheduler, daemon=True).start()

@app.route("/")
def index():
    return redirect(config.homepage)


@app.route("/sync")
@auth.admin_required
def sync():
    app.logger.info("sync requested...")
    try:
        keep.keep.sync()
    except gkeepapi.exception.ResyncRequiredException:
        keep.keep.sync(resync=True)
    redirection.sync()
    label.sync()
    group.sync()
    app.logger.info("synced")
    return redirect(url_for("wall.wall", labels="zmet_index"))

@app.route("/aes")
def aes_page():
    return render_template("aes_page.html")

@app.route("/saltpack/armor")
def saltpack_armor_service():
    message = request.args.get("message")
    if not message:
        abort(400, "Missing base64 encoded `message` argument")

    try:
        message = b64_decode(message)
    except Exception as e:
        abort(422,
            "Base64 decoding. Message:\n" +
            request.args.get("message") + "\n" +
            str(e))

    return saltpack_armor.armor(message)

@app.route("/saltpack/dearmor")
def saltpack_dearmor_service():
    message = request.args.get("message")
    if not message:
        abort(400, "Missing Saltpack encoded `message` argument")

    try:
        message = saltpack_armor.dearmor(message)
    except:
        abort(422, "Saltpack decoding failed. Message: " + request.args.get("message"))

    return b64_encode(message)
