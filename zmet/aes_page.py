from flask import Blueprint, render_template

aes_page_bp = Blueprint("aes", __name__, url_prefix="/aes")


@aes_page_bp.route("/")
def main():
    return render_template("aes_page.html")