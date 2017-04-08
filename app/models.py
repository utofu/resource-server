from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy import Column, DateTime, Index, Integer, String, Text, text, Boolean, ForeignKey
from . import db



Base = declarative_base()
metadata = Base.metadata

class ScopesMixin(object):

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    @scopes.setter
    def scopes(self, value):
        self._scopes = " ".join(value)


class Tokens(Base, ScopesMixin):
    __tablename__ = 'tokens'
    access_token = Column(String(256), primary_key=True)
    access_token_expire_date = Column(DateTime, nullable=False)
    refresh_token = Column(String(256), nullable=True)
    refresh_token_expire_date = Column(DateTime, nullable=False)
    _scopes = Column(Text, nullable=False)
    user_id = Column(String(128), ForeignKey('users.id',ondelete='CASCADE'), nullable=False)
    client_id = Column(String(128), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    grant_code = Column(String(256), ForeignKey('grant_codes.code', ondelete='CASCADE'))


class GrantCodes(Base, ScopesMixin):
    __tablename__ = 'grant_codes'
    code = Column(String(256), primary_key=True)
    expire_date = Column(DateTime, nullable=False)
    is_lapsed = Column(Boolean, default=False, nullable=False)
    _scopes = Column(Text, nullable=False)

    user_id = Column(String(128), ForeignKey('users.id',ondelete='CASCADE'), nullable=False)
    client_id = Column(String(128), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)

    tokens = db.relationship(
        'Tokens',
        primaryjoin="Tokens.grant_code==GrantCodes.code",
        foreign_keys="Tokens.grant_code",
        lazy='dynamic',
        cascade='all, delete-orphan',
        backref="granted_code")


class Users(Base, ScopesMixin):
    __tablename__ = 'users'
    id = Column(String(128), primary_key=True, unique=True)
    password = Column(String(128), nullable=False)
    _scopes = Column(String(128), nullable=False)
    is_restricted = Column(Boolean, nullable=False)

    images = db.relationship(
        'Images',
        primaryjoin="Images.user_id==Users.id",
        foreign_keys="Images.user_id",
        lazy='dynamic',
        cascade='all, delete-orphan',
        backref="user")

    grant_codes = db.relationship(
        'GrantCodes',
        primaryjoin="GrantCodes.user_id==Users.id",
        foreign_keys="GrantCodes.user_id",
        lazy='dynamic',
        cascade='all, delete-orphan',
        backref="user")

    tokens = db.relationship(
        'Tokens',
        primaryjoin="Tokens.user_id==Users.id",
        foreign_keys="Tokens.user_id",
        lazy='dynamic',
        cascade='all, delete-orphan',
        backref="user")

class Images(Base):
    __tablename__ = 'images'
    id = Column(String(128), primary_key=True, unique=True)
    data = Column(Text, nullable=False)
    user_id = Column(String(128), ForeignKey('users.id',ondelete='CASCADE'), nullable=False)


class Clients(Base):
    __tablename__ = 'clients'
    id = Column(String(128), primary_key=True, unique=True)
    secret = Column(String(128), nullable=False)
    name = Column(String(128), nullable=False)
    type = Column(String(128), nullable=False)
    redirect_uri = Column(String(256), nullable=False)

    grant_codes = db.relationship(
        'GrantCodes',
        primaryjoin="GrantCodes.client_id==Clients.id",
        foreign_keys="GrantCodes.client_id",
        lazy='dynamic',
        cascade='all, delete-orphan',
        backref="client")

    tokens = db.relationship(
        'Tokens',
        primaryjoin="Tokens.client_id==Clients.id",
        foreign_keys="Tokens.client_id",
        lazy='dynamic',
        cascade='all, delete-orphan',
        backref="client")
