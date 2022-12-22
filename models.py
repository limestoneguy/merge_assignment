from datetime import datetime
from extensions import db
from sqlalchemy import Column, Date, ForeignKey, UniqueConstraint, Integer, String, Enum
import enum


class UserStatus(enum.Enum):
    ACTIVE = 1
    SUSPENDED = 2


class Roles(db.Model):
    roleId = Column(Integer, primary_key=True)
    roleName = Column(String(50), nullable=False)
    created_at = Column(Date, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.roleId} - {self.roleName} - {self.created_at}"


class User(db.Model):
    sno = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(300), nullable=False)
    role = Column(Integer, ForeignKey('roles.roleId'), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(Date, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('email', name='unique_user_email'),)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.name} - {self.role} - {self.status}"


class Inventory(db.Model):
    sno = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    units = Column(Integer, default=1)
    added_by = Column(Integer, ForeignKey('user.sno'), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.name} - {self.units}"

    def as_dict(self) -> dict:
        return {"sno": self.sno, "name": self.name, "units": self.units, "added_by": self.added_by}


class UserCart(db.Model):
    user_id = Column(Integer, ForeignKey('user.sno'),
                     nullable=False, primary_key=True)
    item_id = Column(Integer, ForeignKey('inventory.sno'),
                     nullable=False, primary_key=True)
    units = Column(Integer, default=1)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.user_id} - {self.item_id} - {self.units}"

    def as_dict(self) -> dict:
        return {"user_id": self.user_id, "item_id": self.item_id, "units": self.units, "created_at": self.created_at, "updated_at": self.updated_at}


class TokenBlockList(db.Model):
    id = Column(Integer, primary_key=True)
    jti = Column(String(200), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"{self.id} - {self.jti}"

    def as_dict(self) -> dict:
        return {"id": self.id, "jti": self.jti}
