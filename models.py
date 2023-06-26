"""SQLAlchemy models for Romaine Calm."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Garden(db.Model):
    """User's garden """

    __tablename__ = 'gardens' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    garden_name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    date_of_creation = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    plants = db.relationship('Plant', secondary='garden_plants', backref='gardens')
    garden_contains = db.relationship('Garden_Plant', cascade='all, delete', backref='gardens')

    


class Plant(db.Model):
    """plants pointing to API"""

    __tablename__= 'plants'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    plant_name_api= db.Column(
        db.Text
    )

    api_id = db.Column(db.Integer) 

class Garden_Plant(db.Model):
    """Mapping plants to gardens"""

    __tablename__ = 'garden_plants' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    garden_id = db.Column(
        db.Integer,
        db.ForeignKey('gardens.id', ondelete='cascade')
    )

    plant_id = db.Column(
        db.Integer,
        db.ForeignKey('plants.id', ondelete='cascade'),
        unique=True
    )

class User(db.Model):
    """User in the systems"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    gardens = db.relationship('Garden', backref='user')
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
