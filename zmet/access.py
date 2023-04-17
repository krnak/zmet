from flask import request
from zmet import crypto
from .label import get_labels, is_public, labels_of
from flask_login import current_user
from .group import get_groups_of


NONE = 0
VIEW = 1
EDIT = 2
ADMIN = 3

def access_to(note):
	if not current_user.is_anonymous and current_user.id == "admin":
		return ADMIN

	if is_public(note):
		return VIEW

	access_symbols = []
	for cookie_name in request.cookies.keys():
		if cookie_name.startswith("view-"):
			token = request.cookies.get(cookie_name)
			try:
				name, salt = crypto.decrypt_token(token)
				assert name == cookie_name[len("view-"):]
				# TODO: check salt
				# TODO: make this more efficient by predetection note acccess symbols
				if name in note.text:
					return VIEW
			except:
				pass

		# TODO: link access

	return NONE


def visible(notes):
	return filter(lambda x: access_to(x) >= VIEW, notes)
