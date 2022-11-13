from flask import (
    request,
    redirect,
    Blueprint,
    flash,
    url_for,
    abort,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
    LoginManager,
    UserMixin,
)
from flask_wtf.csrf import generate_csrf
import urllib.parse
from . import config


def init(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)


auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    url_prefix="/auth",
)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@auth.route("/")
def index():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))
    else:
        return f"""
        <h3>Logged in as { current_user.id }</h3></ br>
        <form action="/auth/logout">
            <input type="submit" value="logout" />
            <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
        """


@auth.route("/login", methods=["GET"])
def login():
    secret = request.args.get("secret")
    next = request.args.get("next")
    if secret:
        if secret == config.guest_secret:
            login_user(User("guest"), remember=True)
        else:
            flash("Invalid secret.")
            return redirect(url_for("auth.login"))

        if next:
            next = urllib.parse.unquote_plus(next)
            return redirect(next)
        else:
            return redirect(url_for("auth.index"))
    else:
        if next:
            next = urllib.parse.quote_plus(next)
        else:
            next = ""
        return f"""
        <h3 class="title">Login</h3>
        <form method="POST" action="/auth/login">
            <input type="password" name="password">
            <input type="hidden" name="next" value="{ next }">
            <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
            <button>Login</button>
        </form>
        """


@auth.route("/login", methods=["POST"])
def login_post():
    pasw = request.form.get("password")
    if pasw == config.admin_pasw:
        login_user(User("admin"), remember=True)
    else:
        flash("Invalid password.")
        return redirect(url_for("auth.login"))

    next = request.form.get("next")
    if next:
        next = urllib.parse.unquote_plus(next)
        return redirect(next)
    else:
        return redirect(url_for("auth.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))


def admin_required(func):
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous or current_user.id != "admin":
            abort(403, "admin rights required")
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
