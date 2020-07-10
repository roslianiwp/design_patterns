from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Members(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guild_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    response_fields = {
        "id": fields.Integer,
        "guild_id": fields.Integer,
        "user_id": fields.Integer,
        "status": fields.Boolean,

        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
    }

    def __init__(self, guild_id, user_id):
        self.guild_id = guild_id
        self.user_id = user_id

    def __repr__(self):
        return "<Members %r>" % self.id