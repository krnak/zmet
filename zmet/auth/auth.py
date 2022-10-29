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
    return """
    <h3 class="title">Login</h3>
    <form method="POST" action="/auth/login">
        <input type="password" name="password">
        <button>Login</button>
    </form>
    """


@auth.route("/login", methods=["POST"])
def login_post():
    pasw = request.form.get("password")

    if pasw != config.zmet_pasw:
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login"))

    login_user(User(), remember=True)
    return redirect(url_for("auth.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))
