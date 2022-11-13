from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from urllib.parse import quote_plus, unquote_plus
from flask_login import login_required

from . import keep
from . import auth
from . import search
from . import links
from . import config
from . import add
from . import img
from . import wall
from . import redirection
from . import label

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

app.register_blueprint(links.links)
app.logger.info("links registered")

app.register_blueprint(add.add)
app.logger.info("add registered")

app.register_blueprint(img.img)
app.logger.info("img registered")

app.register_blueprint(wall.wall_bp)
app.logger.info("wall registered")


@app.route("/")
@login_required
def index():
    return redirect(url_for("wall.wall", labels="zmet_index"))


@app.route("/sync")
@auth.admin_required
def sync():
    app.logger.info("sync requested...")
    keep.keep.sync()
    redirection.sync()
    label.sync()
    app.logger.info("synced")
    return "synced"
