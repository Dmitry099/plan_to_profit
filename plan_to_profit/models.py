import logging
from hashlib import md5
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin, LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from jwt import PyJWTError
from sqlalchemy_utils import PhoneNumber
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "plan_to_profit.login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    clients = db.relationship("Client", backref="user", lazy=True)

    def __str__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except PyJWTError as exc:
            logging.error("Token can't be decoded correctly %s", exc)
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    _phone_number = db.Column(db.Unicode(20))
    phone_country_code = db.Column(db.Unicode(8))
    phone_number = db.orm.composite(
        PhoneNumber, _phone_number, phone_country_code
    )
    email = db.Column(db.String(120), index=True, unique=True)
    contact_details = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return "<Client {}>".format(self.name)
