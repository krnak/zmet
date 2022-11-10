from flask import (
    request,
    redirect,
    Blueprint,
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
        return (
            try_redirect(query.rstrip()) or
            redirect("https://google.com/search?q=" + quote_plus(query))
        )
    else:
        return """
        <form action="/search" method="GET">
            <input type="text" name="q">
            <button>search</button>
        </form>
        """
