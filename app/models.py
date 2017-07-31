import datetime
import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from instance.config import Config

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
        """Initializes the user model
        :param username: A string representing a user's username
        :param password: A string representing the  user password
        :param email: A string representing the user email
        """
        self.username = username
        self.password = password
        self.email = email

    @property
    def password(self):
        """Method prevents the access of password attribute externally"""
        raise AttributeError('You cannot access password')

    @password.setter
    def password(self, password):
        """Generates a hash from the password entered by the user
        :param password: A string representing the user password.
        """
        self.user_password = generate_password_hash(password)

    def verify_password(self, password):
        """Checks the user password against tje hash stored in the database
        to valicate user.
        :param password: A string representing the user password
        """
        return check_password_hash(self.user_password, password)

    def generate_auth_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                Config.SECRET_KEY,
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def verify_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token."
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login."

    def save(self):
        """Saves a user to the database.
        May be creating a user or updating an existing one."""
        db.session.add(self)
        db.session.commit()


class BucketList(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, created_by):
        """Initializes  with name author of the bucketlist.
        :param name: A string representing the name of the bucketlist.
        :param created_by: An integer representing the id of the bucketlist's author.
        """
        self.name = name
        self.created_by = created_by

    def save(self):
        """Saves a bucketlist into the database.
        Could be editing a new bucketlist or editing a pre existing one."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        """Fetches all the bucketlists from the database"""
        return BucketList.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<BucketList: {}>".format(self.name)


class BucketListItem(db.Model):
    """This class represents the bucketlist_item table"""
    __tablename__ = 'bucketlistitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(BucketList.id))

    def __init__(self, name, bucketlist_id):
        """
        Initializes bucketlist item.
        :param name: A string representing the name of the bucketlist item.
        :param bucketlist_id: A unique integer identifier for the bucketlist item.
        """
        self.name = name
        self.bucketlist_id = bucketlist_id

    def save(self):
        """Saves all the bucktlist items to the database."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_items():
        """Method retrieves bucketlist item from the database
        based on the bucketlist id."""
        return BucketListItem.query.filter_by(bucketlist_id=BucketList.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
