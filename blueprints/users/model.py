from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), default='')
    email = db.Column(db.String(255), unique=True, nullable=False)
    salt = db.Column(db.String(255), default='')
    avatar = db.Column(db.String(255), default='')
    status = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    response_fields = {
        "id": fields.Integer,
        "username": fields.String,
        "password": fields.String,
        "name": fields.String,
        "email": fields.String,
        "avatar": fields.String,
        "status": fields.Boolean,

        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
    }

    jwt_claim_fields = {
        "id": fields.Integer,
        "username": fields.String,
        "is_user": fields.Boolean,
        "status": fields.Boolean
    }

    def __init__(self, username, email, salt, password):
        self.username = username
        self.email = email
        self.salt = salt
        self.password = password

    def __repr__(self):
        return "<Users %r>" % self.id
