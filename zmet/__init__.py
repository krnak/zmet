from flask import Flask, redirect, url_for

from . import keep
from .auth import auth
from . import config

keep.init()

app = Flask(__name__)
app.secret_key = config.app_secret_key

app.register_blueprint(auth.auth)
auth.init(app)
print("auth blueprint registered")


@app.route("/")
def index():
    return redirect(url_for("auth.index"))
