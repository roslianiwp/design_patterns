from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref

class Conversation(db.Model):
    __tablename__ = "conversation"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), default='')
    description = db.Column(db.String(255), default='')
    category = db.Column(db.String(255), default='general')
    banner = db.Column(db.String(255), default='')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    response_fields = {
        "id": fields.Integer,
        "name": fields.String,
        "description": fields.String,
        "banner": fields.String,
        "category": fields.String,
        "owner_id": fields.Integer,
        "status": fields.Boolean,
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
    }

    def __init__(self, name, description, category, banner, owner_id):
        self.name = name
        self.description = description
        self.category = category
        self.banner = banner
        self.owner_id = owner_id

    def __repr__(self):
        return "<Conversation %r>" % self.id