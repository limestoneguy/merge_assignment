from flask import Blueprint, request, jsonify
from models import *
from middlewares.userAuth import rbac_auth
from extensions import bcrypt
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from operator import itemgetter
from exceptions import EmailExistsError, GenericAPIError
from routes.cart import route as cart_route

route = Blueprint('user', __name__)
route.register_blueprint(cart_route, url_prefix='/cart')


@route.post('/')
@jwt_required()
@rbac_auth(permissions=["admin"])
def create_user():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    current_user = get_jwt_identity()
    try:
        name, email, password, role = itemgetter(
            'name', 'email', 'password', 'role')(request.get_json())
        roleCode = Roles.query.filter_by(roleName=role).first()
        checkEmail = User.query.filter_by(email=email).first()
        if not roleCode:
            raise KeyError
        if checkEmail:
            raise EmailExistsError
    except KeyError:
        return jsonify({"code": 401, "message": 'Missing Parameters'})
    except EmailExistsError:
        return jsonify({"code": 401, "message": 'Email already exists'})

    user = User(name=name, email=email,
                password=bcrypt.generate_password_hash(password=password, rounds=5), role=roleCode.roleId)
    db.session.add(user)
    db.session.commit()
    return jsonify(current_user)


@route.get('/login')
def user_login():
    email = request.args.get('email')
    password = request.args.get('password')
    user: User = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"response": False, "message": "Email not found"}), 401
    hashed_password = bcrypt.check_password_hash(
        pw_hash=user.password, password=password)
    if not hashed_password:
        return jsonify({"response": False, "message": "Username or Password is invalid"}), 401

    if user.status == UserStatus.SUSPENDED:
        raise GenericAPIError(
            message="Acccount has been suspended", status_code=401)

    role = Roles.query.join(User).filter(User.email == user.email).first()
    access_token = create_access_token(
        identity={"email": user.email, "role": role.roleName, "name": user.name})
    return jsonify(access_token)


@route.post('/suspend')
@jwt_required()
@rbac_auth(permissions=['admin'])
def suspend_user():
    email = request.get_json().get('email')
    userDetails = User.query.filter_by(email=email).first()
    if not userDetails:
        raise GenericAPIError(message="User not found", status_code=404)
    userDetails.status = UserStatus.SUSPENDED if userDetails.status == UserStatus.ACTIVE else UserStatus.ACTIVE
    db.session.commit()
    return jsonify({"message": f'{email} status changed to {userDetails.status}'})
