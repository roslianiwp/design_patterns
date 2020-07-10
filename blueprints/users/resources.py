from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
import json
from .model import Users
from blueprints import db, app, user_required
from sqlalchemy import desc
import hashlib
from datetime import datetime
import uuid
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

bp_user = Blueprint('user', __name__)
api = Api(bp_user)


class UsersRegistrationResource(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        parser.add_argument("email", location="json", required=True)
        args = parser.parse_args()

        salt = uuid.uuid4().hex
        encoded = ('%s%s' % (args['password'], salt)).encode('utf-8')
        hash_pass = hashlib.sha512(encoded).hexdigest()

        user = Users(args['username'], args['email'], salt, hash_pass)
        db.session.add(user)
        db.session.commit()

        app.logger.debug('DEBUG : %s', user)

        return marshal(user, Users.response_fields), 200, {'Content-Type': 'application/json'}


class UsersResource(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @user_required
    def get(self):
        user_claims = get_jwt_claims()
        qry = Users.query.get(user_claims["id"])

        return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}

    @user_required
    def delete(self):
        user_claims = get_jwt_claims()
        qry = Users.query.get(user_claims["id"])
        qry.status = False
        db.session.commit()

        return {"message": "Succesfully Deactivated"}, 200, {"Content-Type": "application/json"}


api.add_resource(UsersRegistrationResource, '/register')
api.add_resource(UsersResource, '/info')
