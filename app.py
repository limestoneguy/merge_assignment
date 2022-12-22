from sqlite3 import IntegrityError
from flask import Flask, render_template, request, jsonify
from exceptions import GenericAPIError
from extensions import db, bcrypt, jwt
from models import *
from routes.user import route as user_route
from routes.items import route as items_route
import app_jwt
from init import initialzeRoles

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///merge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'Some_Secret_ENV_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 10 * 60 * 60 * 60
app.register_blueprint(user_route, url_prefix='/api/user')
app.register_blueprint(items_route, url_prefix='/api/item')

bcrypt.init_app(app)
db.init_app(app)
jwt.init_app(app)


@app.errorhandler(GenericAPIError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(KeyError)
def handle_invalid_usage(error):
    response = jsonify(
        {"code": "bad_request", "message": "Required Parameters not found"})
    response.status_code = 400
    return response


@app.errorhandler(IntegrityError)
def handle_sql_usage(error):
    response = jsonify(
        {"code": "bad_request", "message": "Error on sql statement"})
    response.status_code = 400
    return response


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        if True:
            db.drop_all()
            db.create_all()
            hashed_password = bcrypt.generate_password_hash(
                password='user123', rounds=5)
            admin_user = User(name='Rishabh Kanaujia',
                              email="kanaujia.rishabh@gmail.com", password=hashed_password, role=1)
            normal_user = User(name='Sourav',
                               email="sourav@gmail.com", password=hashed_password, role=2)
            normal_user_suspend = User(name='Aditya',
                                       email="aditya@gmail.com", password=hashed_password, role=2)
            db.session.add(admin_user)
            db.session.add(normal_user)
            db.session.add(normal_user_suspend)
            db.session.commit()
        initialzeRoles()
    app.run(debug=True, port=80)
