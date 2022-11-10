from flask import (
    request,
    redirect,
    Blueprint,
    url_for,
)
from flask_login import login_required
from urllib.parse import quote_plus

from .redirection import try_redirect

search = Blueprint("search", __name__, url_prefix="/search")


@search.route("/")
@login_required
def index():
    query = request.args.get("q")
    if query:
        red = try_redirect(query.rstrip())
        if red:
            return red
        if query.startswith("s "):
            return redirect(url_for("view.wall", q=query[2:]))
        if query.startswith("#"):
            return redirect(url_for("view.wall", label=query[1:]))
        return redirect("https://google.com/search?q=" + quote_plus(query))
    else:
        return """
        <form action="/search" method="GET">
            <input type="text" name="q">
            <button>search</button>
        </form>
        """
