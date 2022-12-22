from flask import Blueprint, request, jsonify
from models import *
from middlewares.userAuth import rbac_auth
from flask_jwt_extended import jwt_required, get_jwt_identity
from operator import itemgetter
from exceptions import GenericAPIError, ItemNotFoundError

route = Blueprint('item', __name__)


@route.post('/')
@jwt_required()
@rbac_auth(['admin'])
def create_item():
    if not request.is_json:
        raise GenericAPIError(message='Required Params not found')
    name, units = itemgetter('name', 'units')(request.get_json())
    current_user = dict(get_jwt_identity())
    user = User.query.filter_by(email=current_user.get('email')).first()
    item = Inventory(name=name, units=units, added_by=user.sno)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item added successfully"})


@route.get('/')
@jwt_required()
@rbac_auth(permissions=['user', 'admin'])
def get_all_items():
    items = Inventory.query.all()
    return jsonify({"message": "Something", "items": [item.as_dict() for item in items]})


@route.delete('/<itemId>')
@jwt_required()
@rbac_auth(['admin'])
def delete_item(itemId):
    item = Inventory.query.filter_by(sno=itemId).first()
    if not item:
        raise GenericAPIError(status_code=404, message="Item not found", payload={
                              "code": "item_not_found"})
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"})
