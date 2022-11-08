from flask import Flask, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required

from . import keep
from .auth import auth
from . import search
from . import links
from . import config
from . import add
from . import img
from .view import view

keep.init()

app = Flask(__name__)
app.secret_key = config.app_secret_key
app.debug = True

csrf = CSRFProtect()
csrf.init_app(app)

app.register_blueprint(auth.auth)
auth.init(app)
print("auth registered")

app.register_blueprint(search.search)
print("search registered")

app.register_blueprint(links.links)
print("links registered")

app.register_blueprint(add.add)
print("add registered")

app.register_blueprint(img.img)
print("img registered")

app.register_blueprint(view.view)
print("view registered")


@app.route("/")
def index():
    return redirect(url_for("search.index"))


@app.route("/sync")
@login_required
def sync():
    print("sync requested...")
    keep.keep.sync()
    print("synced")
    return "synced"
