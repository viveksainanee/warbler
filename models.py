"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class FollowersFollowee(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = 'follows'

    followee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class Thread(db.Model):
    """Connection from one user to another for a dm """

    __tablename__ = 'threads'

    id = db.Column(
        db.Integer, autoincrement=True, primary_key=True
    )

    user1_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"))

    user2_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"))

    db.UniqueConstraint('user1_id', 'user2_id')

    user1 = db.relationship("User", foreign_keys=[user1_id])
    user2 = db.relationship("User", foreign_keys=[user2_id])

    dms = db.relationship("DM", backref="thread")


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message', backref='user', lazy='dynamic')
    reacted_messages = db.relationship(
        'Message', secondary="reactions", backref="users_who_reacted")
    reactions = db.relationship(
        'Reaction', backref='user', cascade="all,delete-orphan")

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(FollowersFollowee.follower_id == id),
        secondaryjoin=(FollowersFollowee.followee_id == id),
        backref=db.backref('following', lazy='dynamic'),
        lazy='dynamic')

    people_talking_to = db.relationship(
        "User",
        secondary="threads",
        primaryjoin=(Thread.user1_id == id),
        secondaryjoin=(Thread.user2_id == id),
        backref=db.backref('people_talking_to_me', lazy='dynamic'),
        lazy='dynamic')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        return bool(self.followers.filter_by(id=other_user.id).first())

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        return bool(self.following.filter_by(id=other_user.id).first())

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
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

    def get_reactions(self, reaction_type):
        return {message_id[0] for message_id in db.session.query(Reaction.message_id).filter(
            Reaction.reaction_type == reaction_type, Reaction.user_id == self.id).all()}

    def get_my_messages(self):
        return {message_id[0] for message_id in db.session.query(Message.id).filter(Message.user_id == self.id).all()}


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    reaction = db.relationship('Reaction', backref='message')


class Reaction(db.Model):
    """reactions"""
    __tablename__ = 'reactions'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, primary_key=True)
    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='CASCADE'),
        nullable=False, primary_key=True)
    reaction_type = db.Column(
        db.String, nullable=False, primary_key=True)


class DM(db.Model):
    """the exact message, connected to a thread"""
    __tablename__ = 'dms'

    id = db.Column(
        db.Integer,
        primary_key=True, autoincrement=True
    )

    text = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    thread_id = db.Column(
        db.Integer,
        db.ForeignKey('threads.id', ondelete='CASCADE'),
        nullable=False,
    )

    author = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    user = db.relationship("User", backref="dm")


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
