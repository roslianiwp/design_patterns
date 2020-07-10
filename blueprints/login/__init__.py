from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from functools import wraps
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

from ..users.model import Users
import hashlib

bp_login = Blueprint('login', __name__)
api = Api(bp_login)


class CreateTokenResource(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="args", required=True)
        parser.add_argument("password", location="args", required=True)
        args = parser.parse_args()

        qry_user = Users.query.filter_by(username=args['username']).first()

        if qry_user is not None:
            user_salt = qry_user.salt
            encoded = ('%s%s' % (args['password'], user_salt)).encode('utf-8')
            hash_pass = hashlib.sha512(encoded).hexdigest()

            user_claims_data = marshal(qry_user, Users.jwt_claim_fields)
            if hash_pass == qry_user.password and qry_user.username == args['username']:
                user_claims_data["is_user"] = True

            token = create_access_token(identity=args['username'], user_claims=user_claims_data)
            return {'token': token}, 200

        else:
            return {'status': 'UNAUTHORIZED', 'message': 'invalid key or secret'}, 404


api.add_resource(CreateTokenResource, '')
