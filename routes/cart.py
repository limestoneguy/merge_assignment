from operator import itemgetter
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from exceptions import GenericAPIError

from middlewares.userAuth import rbac_auth
from models import *


route = Blueprint('cart', __name__)


@route.post('/')
@jwt_required()
@rbac_auth(permissions=['user', 'admin'])
def add_to_cart():
    if not request.is_json:
        raise GenericAPIError(message="Missing JSON in request")

    itemId, units = itemgetter("itemId", "units")(request.get_json())
    item = Inventory.query.filter_by(sno=itemId).first()

    if not item:
        raise GenericAPIError(message="Item not found", status_code=404)

    if not item.units - units > 0:
        raise GenericAPIError(message="Not Enough items in stock")

    current_user = dict(get_jwt_identity())
    userDetails = User.query.filter_by(email=current_user.get("email")).first()
    item.units = item.units - units
    cartData = UserCart(user_id=userDetails.sno, item_id=item.sno, units=units)
    db.session.add(cartData)
    db.session.commit()
    return jsonify({"message": "Item Added to your cart"})


@route.delete('/<itemId>')
@jwt_required()
@rbac_auth(permissions=['user', 'admin'])
def remove_from_cart(itemId):
    user_details = User.query.filter_by(
        email=get_jwt_identity().get("email")).first()

    cart_item = UserCart.query.filter_by(
        item_id=itemId, user_id=user_details.sno).first()

    if not cart_item:
        raise GenericAPIError(
            message="Item in cart not found", status_code=404)

    inventory_item = Inventory.query.get(cart_item.item_id)
    inventory_item.units = inventory_item.units + cart_item.units
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item Removed to your cart"})


@route.get('/')
@jwt_required()
@rbac_auth(permissions=['user', 'admin'])
def view_cart():
    return jsonify([])
