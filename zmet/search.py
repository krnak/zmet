from flask import (
    request,
    redirect,
    Blueprint,
)
from urllib.parse import quote_plus

from .redirection import try_redirect
from .auth import admin_required

search = Blueprint("search", __name__, url_prefix="/search")


@search.route("/")
@admin_required
def index():
    query = request.args.get("q")
    if query:
        return (
            try_redirect(query.rstrip()) or
            redirect("https://www.google.com/search?q=" + quote_plus(query))
        )
    else:
        return """
        <form action="/search" method="GET">
            <input type="text" name="q">
            <button>search</button>
        </form>
        """
