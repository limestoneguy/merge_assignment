from extensions import db
from models import *


def initialzeRoles():
    roles = ['admin', 'user']
    dbRoles = Roles.query.all()
    if len(dbRoles) < len(roles):
        print('Initailizing all Roles in DB')
        for roleName in roles:
            role = Roles(roleName=roleName)
            db.session.add(role)
            db.session.commit()
    else:
        print('Roles already assigned in DB')
