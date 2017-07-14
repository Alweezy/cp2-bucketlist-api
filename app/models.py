from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    """This class represents the user table."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    user_password = db.Column(db.String(255), nullable=False)
    bucketlists = db.relationship('BucketList', order_by="BucketList.id",
                                  cascade="all,delete-orphan")

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    @property
    def password(self):
        raise AttributeError('You cannot access password')

    @password.setter
    def password(self):
        self.user_password = generate_password_hash(self.password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Bucketlist(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name):
        """initialize with name."""
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)


class BucketListItem(db.Model):
    """This class represents the bucketlist_item table"""
    __tablename__ = 'bucketlistitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(Bucketlist.id))

    def __init__(self, name, bucketlist_id):
        """Initialize with name and bucketlist_id"""
        self.name = name
        self.bucketlist_id = bucketlist_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_items():
        return BucketListItem.query.filter_by(bucketlist_id=Bucketlist.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
