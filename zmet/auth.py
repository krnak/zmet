from flask import (
    request,
    redirect,
    Blueprint,
    flash,
    url_for,
    abort,
    make_response,
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
from datetime import datetime
from . import config
from . import crypto
from .group import get_link_groups, get_groups
from .label import get_labels

ANYM_USERS_CACHE = set()

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


def redirect_to_next():
    next = request.args.get("next") or request.form.get("next")
    if next:
        try:
            next = urllib.parse.unquote_plus(next)
            resp = redirect(next)
        except ValueError:
            resp = "Invalid url encoding."
    else:
        return ""


@auth.route("/")
def index():
    if current_user.is_anonymous:
        return f"""
            <h3>Not logged in</h3><br />
            <a href="{ url_for("auth.login") }">
               <button>Login</button>
            </a>
        """
    else:
        return f"""
        <h3>Logged in as @{ current_user.id }</h3></ br>
        <form action="/auth/logout">
            <input type="submit" value="logout" />
            <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
        """


@auth.route("/login", methods=["GET"])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for("auth.index"))
    token = request.args.get("token")
    if token:
        return login_by_token(token)
    else:
        next = request.args.get("next")
        return f"""
        <h3 class="title">Login</h3>
        <form method="POST" action="/auth/login{ "?next=" + next if next else "" }">
            <input type="text" name="token">
            <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
            <button>Login</button>
        </form>
        """


@auth.route("/login", methods=["POST"])
def login_post():
    token = request.form.get("token")
    return login_by_token(token)


"""
if type == crypto.GROUP:
    group = get_link_groups().get(name)
    if not group:
        abort(404, "group not found")
    group.verify_salt(salt)
    username = "anym" + datetime.now().strftime("%y%m%d%H%M%S")
    if username in ANYM_USERS_CACHE:
        abort(403, "try again")
    ANYM_USERS_CACHE.add(username)
    group.add_member(username)
    token = crypto.gen_user_token(username)
    return login_by_token(token, next)
"""

def login_by_token(token):
    if token == config.admin_pasw:
        login_user(User("admin"), remember=True)
        return redirect(url_for("auth.index"))

    resp = redirect_to_next() or redirect("/")
    resp = make_response(resp)

    try:
        name, salt = crypto.decrypt_token(token)
        if name[0] == "@":
            resp.set_cookie(f"view-{ name }", token)
            for group in get_groups():
                if name in group.users:
                    token = crypto.gen_token(f"^{ group.name }", group.salt)
                    resp.set_cookie(f"view-^{ group.name }", token.decode())
            login_user(User(name), remember=True)
        elif name[0] == "#":
            resp.set_cookie(f"view-{ name }", token)
        else:
            abort(404)
    except ValueError:
        flash("Invalid token.")
        return redirect(url_for("auth.login"))

    return resp


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    next = request.args.get("next")
    return redirect_to_next() or redirect("/")


def admin_required(func):
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous or current_user.id != "admin":
            abort(403, "admin rights required")
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@auth.route("/add", methods=["GET"])
@admin_required
def add_user():
    return f"""
    <h3 class="title">Add user</h3>
    <form method="POST" action="/auth/add">
        username <input type="text" name="name"><br />
        groups <input type="text" name="groups"><br />
        redirection <input type="text" name="next"><br />
        <input type="hidden" name="next" value="">
        <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        <button>Login</button>
    </form>
    """


@auth.route("/add", methods=["POST"])
@admin_required
def add_user_post():
    name = request.form.get("name")
    assert name is not None
    try:
        for group in request.form.get("groups").split(","):
            if group == "":
                continue
            get_groups().get(group).add_member(name)
    except Exception as e:
        abort(400, f"groups error: {str(e)}")
    token = crypto.gen_token(f"@{name}")
    url = config.url + "/auth/login?token=" + token.decode()
    next = request.form.get("next")
    if next:
        url += "&next=" + urllib.parse.quote_plus(next)
    return url


@auth.route("/tokens")
@admin_required
def tokens():
    links = []
    for name, label in get_labels().items():
        if "view_token" in label.labels:
            continue
        token = crypto.gen_label_token(name)
        url = config.url + "/auth/login?token=" + token.decode()
        links.append(f"<li>#{ name }: { url }</li>")
    return "<ul>" + "".join(links) + "</ul>"

"""
@auth.route("/groups")
@admin_required
def groups():
    links = []
    for name, group in get_link_groups().items():
        token = crypto.gen_group_token(name)
        url = config.url + "/auth/login?token=" + token.decode()
        links.append(f"<li>{ name }: { url }</li>")
    return "<ul>" + "".join(links) + "</ul>"
"""

