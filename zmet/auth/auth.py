from flask import (
    request,
    redirect,
    Blueprint,
    flash,
    url_for,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
    LoginManager,
)
import urllib.parse
from .. import config
from .user import User


def init(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User()


auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    url_prefix="/auth",
)


@auth.route("/")
def index():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))
    else:
        return """
        <h3>Logged in</h3></ br>
        <form action="/auth/logout">
            <input type="submit" value="logout" />
        </form>
        """


@auth.route("/login")
def login():
    next = request.args.get("next")
    if next:
        next = urllib.parse.quote_plus(next)
    else:
        next = ""
    return f"""
    <h3 class="title">Login</h3>
    <form method="POST" action="/auth/login">
        <input type="password" name="password">
        <input type="hidden" name="next" value="{next}">
        <button>Login</button>
    </form>
    """


@auth.route("/login", methods=["POST"])
def login_post():
    pasw = request.form.get("password")
    next = request.form.get("next")
    # TODO: csfr protection

    if pasw != config.zmet_pasw:
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login"))

    login_user(User(), remember=True)

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
