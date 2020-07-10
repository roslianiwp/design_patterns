from flask import Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from flask_restful import Resource, Api, reqparse, marshal, inputs
from blueprints import db, app, user_required
from sqlalchemy import desc
from .model import Members
from blueprints.conversation.model import Conversation
import hashlib
import json
import uuid

bp_member = Blueprint('member', __name__)
api = Api(bp_member)


class MembersResources(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @user_required
    def get(self):
        claims = get_jwt_claims()
        user_id = claims['id']
        members = Members.query.filter_by(user_id=user_id)
        members = members.filter_by(status=True)
        members = members.order_by(desc(Members.updated_at))
        members = members.all()

        guilds = []
        listID = []
        for member in members:
            guild = Conversation.query.filter_by(id=member.guild_id).first()
            marshalGuild = marshal(guild, Conversation.response_fields)
            marshalMember = marshal(member, Members.response_fields)
            marshalMember["guild_id"] = marshalGuild

            if guild.id not in listID:
                guilds.append(marshalMember)

            listID.append(guild.id)

        return guilds, 200


class MembersDetailResources(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @user_required
    def get(self, id=None):
        qry = Members.query.get(id)
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, Members.response_fields), 200

        app.logger.debug('DEBUG : Members not found!')
        return {'status': 'NOT_FOUND'}, 404

    @user_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("guild_id", location="json", required=True)
        data = parser.parse_args()

        claims = get_jwt_claims()
        user_id = claims['id']

        member = Members(data['guild_id'], user_id)
        db.session.add(member)
        db.session.commit()

        app.logger.debug('DEBUG : %s', member)
        return marshal(member, Members.response_fields), 200, {'Content-Type': 'application/json'}

    @user_required
    def delete(self, id=None):
        qry = Members.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'DELETED'}, 200


api.add_resource(MembersResources, "", "/list")
api.add_resource(MembersDetailResources, "", "/<int:id>")
