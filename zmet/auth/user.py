from flask_login import UserMixin


class User(UserMixin):
    """User singleton."""
    def __init__(self):
        self.id = "user"
