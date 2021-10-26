"""SQLAlchemy models for 4cast."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """ User in the system """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True)

    first_name = db.Column(db.Text, nullable=False)

    last_name = db.Column(db.Text, nullable=False)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    home_location = db.Column(db.Text, nullable=True)

    daily_emails = db.Column(db.Boolean, default=False)

    locations = db.relationship('Location')

    def full_name(self):
        return self.first_name + " " + self.last_name

    @classmethod
    def signup(cls, first_name, last_name, email, password, home_location, daily_emails):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_pwd,
                home_location=home_location,
                daily_emails=daily_emails
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Location(db.Model):
    """ User's favorited locations """

    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    location = db.Column(db.Text, nullable=False)

def connect_db(app):
    """ Connect this database to provided Flask app """

    db.app = app
    db.init_app(app)