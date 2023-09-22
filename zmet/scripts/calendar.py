from ..keep import keep
from .refs import find_ref
import datetime

WEEK_DAYS = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]

def day_ref(date):
	return "d" + date.strftime("%y%m%d")

def week_ref(date):
	date -= datetime.timedelta(days=date.weekday())
	return "t" + date.strftime("%y%m%d")

def create_day_note(date, day_name, text=""):
	return keep.createNote(
		title=f'🌅 { day_name } { date.strftime("%d.%m.%Y") } &{ day_ref(date) }',
		text=text,
	)

def create_weekly_note(ref):
	yield 'creating weekly note for ref &' + ref
	keep.sync()
	try:
		note = find_ref(ref)
		yield f'this note already exists: "{ note.title }"'
		return
	except ValueError:
		pass

	date0 = datetime.date(2000 + int(ref[1:3]), int(ref[3:5]), int(ref[5:7]))
	dates = [date0 + datetime.timedelta(days=i) for i in range(7)]
	lines = []
	for date, day_name in zip(dates, WEEK_DAYS):
		dref = day_ref(date)
		lines.append(f'== {day_name[:2]} { date.strftime("%d") } == *{ dref }')
		try:
			day_note = find_ref(dref)
			for line in day_note.text.split("\n"):
				lines.append(line)
		except ValueError:
			create_day_note(date, day_name)

	week_note = keep.createNote(
		title=f'🗓️ týden { date0.strftime("%d.%m.%Y") } &{ week_ref(date0) }',
		text="\n".join(lines)
	)

	keep.sync()

	yield f'created note: 🗓️ týden { date0.strftime("%d.%m.%Y") }'


def create_next_6_weekly_notes():
	today = datetime.date.today()
	week_day = today.weekday()
	next_monday = today + datetime.timedelta(days=(-week_day)%7)
	for i in range(6):
		monday_i = next_monday + datetime.timedelta(days=7*i)
		ref = week_ref(monday_i)
		yield from create_weekly_note(ref)


def pin_todays_note():
	yield "pinning today's note"
	keep.sync()
	today = datetime.date.today()
	today_ref = day_ref(today)
	try:
		note = find_ref(today_ref)
		yield "day note exists"
	except ValueError:
		note = create_day_note(today, WEEK_DAYS[today.weekday()])
		yield "day note created"
	note.pinned = True
	keep.sync()
	yield "pinned"


def unpin_yesterdays_note():
	yield "unpining yesterdays's note"
	keep.sync()
	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)
	try:
		note = find_ref(day_ref(yesterday))
		note.pinned = False
		yield "yesterday's note unpinned"
		keep.sync()
	except ValueError:
		yield "yesterday's note not found"
