from flask import Blueprint, Response, redirect, url_for, request, current_app, render_template
from . import calendar
from . import mosaic
from ..auth import admin_required
import threading
import time
import schedule
import datetime

scripts_bp = Blueprint("scripts", __name__, url_prefix="/scripts", template_folder="templates")

@scripts_bp.route("/")
@admin_required
def index():
	return f"""
	<html>
	<head></head>
	<body>
		<h2>scripts</h2><br />
		<ul>
			<li>
			<a href="{ url_for("scripts.update_mosaics") }">
			   <button>update mosaics</button>
			</a>
			</li>
			<li>
			<form action="{ url_for("scripts.create_weekly_note") }" method="get">
				<input type="submit" value="create weekly note" name="Submit"/>
				for week <input type="text" name="ref">
			</form>
			</li>
			<li>
			<a href="{ url_for("scripts.create_next_6_weekly_notes") }">
			   <button>create_next_6_weekly_notes</button>
			</a>
			</li>
		</ul>
	</body>
	</html>
	"""

def eval_script(script):
	messages = []
	for message in script:
		messages.append(message)
		current_app.logger.info(message)
	return "<br />".join(messages)

@scripts_bp.route("/update_mosaics")
@admin_required
def update_mosaics():
	return eval_script(mosaic.update_mosaics())


@scripts_bp.route("/create_weekly_note")
@admin_required
def create_weekly_note():
	ref = request.args.get("ref")
	if not ref:
		return "missing ref argument"
	return eval_script(calendar.create_weekly_note(ref))


@scripts_bp.route("/create_next_6_weekly_notes")
@admin_required
def create_next_6_weekly_notes():
	return eval_script(calendar.create_next_6_weekly_notes())


def scripts_scheduler(interval=60):
	schedule.every(10).minutes.do(
		lambda: eval_script(
			mosaic.update_mosaics()
		)
	)
	schedule.every().sunday.at("03:00").do(
		lambda: eval_script(
			calendar.create_next_6_weekly_notes()
		)
	)
	schedule.every().day.at("03:00").do(
		lambda: eval_script(
			calendar.pin_todays_note()
		)
	)
	schedule.every().day.at("03:00").do(
		lambda: eval_script(
			calendar.unpin_yesterdays_note()
		)
	)

	while True:
		schedule.run_pending()
		time.sleep(interval)