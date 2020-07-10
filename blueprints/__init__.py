import config
import json
import os

from functools import wraps
from flask_jwt_extended import JWTManager, get_jwt_claims, verify_jwt_in_request
from flask import Flask, request
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

###############################################################
app = Flask(__name__)
cors = CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            supports_credentials=True, intercept_exceptions=False)

jwt = JWTManager(app)


def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims["is_user"]:
            return {"status": "FORBIDDEN", "message": "Registered Users Only!"}, 403
        return fn(*args, **kwargs)

    return wrapper


my_flask = os.environ.get('FLASK_ENV', 'Production')
if my_flask == 'Production':
    app.config.from_object(config.ProductionConfig)
elif my_flask == 'Testing':
    app.config.from_object(config.TestingConfig)
else:
    app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.before_request
def before_request():
    if request.method != 'OPTIONS':  # <-- required
        pass
    else:
        return {}, 200, {'Access-Control-Allow-Origin': '*',
                         'Access-Control-Allow-Headers': '*',
                         'Access-Control-Allow-Methods': '*',
                         }


# log handler
@app.after_request
def after_request(response):
    try:
        requestData = request.get_json()
    except Exception as e:
        requestData = request.args.to_dict()
    if response.status_code == 200:
        app.logger.info("REQUEST_LOG\t%s",
                        json.dumps({
                            'status_code': response.status_code,
                            'method': request.method,
                            'code': response.status,
                            'uri': request.full_path,
                            'request': requestData,
                            'response': json.loads(response.data.decode('utf-8'))
                        })
                        )
    else:
        app.logger.error("REQUEST_LOG\t%s",
                         json.dumps({
                             'status_code': response.status_code,
                             'method': request.method,
                             'code': response.status,
                             'uri': request.full_path,
                             'request': requestData,
                             'response': json.loads(response.data.decode('utf-8'))
                         })
                         )
    return response


# Import Blueprint
from blueprints.users.resources import bp_user
from blueprints.login import bp_login
from blueprints.conversation.resources import bp_conversation
from blueprints.members.resources import bp_member
from blueprints.messages.resources import bp_message

# Register Blueprint
app.register_blueprint(bp_user, url_prefix='/users')
app.register_blueprint(bp_login, url_prefix='/users/login')
app.register_blueprint(bp_conversation, url_prefix='/conversation')
app.register_blueprint(bp_member, url_prefix='/members')
app.register_blueprint(bp_message, url_prefix='/messages')

db.create_all()
