from flask import Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from flask_restful import Resource, Api, reqparse, marshal, inputs
from blueprints import db, app, user_required
from sqlalchemy import desc
from datetime import datetime
from .model import Messages
from blueprints.conversation.model import Conversation
from blueprints.users.model import Users
import hashlib
import json
import uuid

bp_message = Blueprint('message', __name__)
api = Api(bp_message)


class MessagesResources(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("guild_id", location="json", required=True)
        parser.add_argument("content", location="json", required=True)
        args = parser.parse_args()

        claims = get_jwt_claims()
        user_id = claims['id']

        message = Messages(args["guild_id"], user_id, args["content"])

        message.created_at=datetime.now()

        db.session.add(message)
        db.session.commit()

        app.logger.debug('DEBUG: Success')
        return marshal(message, Messages.response_fields), 200

    @user_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=10000)
        parser.add_argument("guild_id", location="args")

        args = parser.parse_args()
        offset = (args['p'] * args['rp']) - args['rp']

        claims = get_jwt_claims()
        user_id = claims['id']

        messages = Messages.query.filter_by(status=True)
        messages = messages.filter_by(guild_id=args["guild_id"])

        data = []
        for msg in messages.limit(args['rp']).offset(offset).all():
            # user = Users.query.filter_by(id=msg.user_id).first()
            # marshalUsers = marshal(user, Users.response_fields)
            marshalMessage = marshal(msg, Messages.response_fields)
            # marshalMessage["user_id"] = marshalUsers
            data.append(marshalMessage)

        return data, 200

    @user_required
    def delete(self, id=None):
        qry = Messages.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'DELETED'}, 200


api.add_resource(MessagesResources, "", "/<int:id>")
