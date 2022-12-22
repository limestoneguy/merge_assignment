from extensions import jwt
from models import TokenBlockList


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload['jti']
    token = TokenBlockList.query.filter_by(jti=jti).first()
    return token is not None
