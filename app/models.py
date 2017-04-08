from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, scoped_session
from sqlalchemy import Column, DateTime, Index, Integer, String, Text, text, Boolean, ForeignKey
from datetime import datetime
try: 
    from . import db
except ValueError:
    import sys
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = sys.argv[1]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy()
    db.init_app(app)


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

    @classmethod
    def fetch_by_access_token(cls, access_token):
        return cls.query.filter_by(access_token=access_token).filter(cls.access_token_expire_date > datetime.now()).first()


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
    is_restricted = Column(Boolean, nullable=False, default=False)

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

    @classmethod
    def new_user(cls, user_id, user_password):
        # type: (str, str, List[str]) -> Users
        scopes = ['add_image', 'get_image', 'list_image', 'delete_image']
        return cls(id=user_id, user_password=user_password, _scopes=" ".join(scopes))

    @classmethod
    def new_restricted_user(cls, user_id, user_password):
        scopes = ['list_image']
        return cls(id=user_id, password=user_password, _scopes=" ".join(scopes))

    @classmethod
    def fetch(cls, user_id, user_password):
        # type: (str, str) -> Union[Users, None]
        return cls.query.filter_by(id=user_id, user_password=user_password).first()

    def create_image(self, data):
        # type: (str) -> Images
        return Images(user_id=self.id, data=data)

    def to_dict(self):
        return {
            'user_id':  self.id,
            'scopes': self.scopes
                }

class Images(Base):
    __tablename__ = 'images'
    id = Column(String(128), primary_key=True)
    data = Column(Text, nullable=False)
    user_id = Column(String(128), ForeignKey('users.id',ondelete='CASCADE'), nullable=False)

    @classmethod
    def new(cls, user_id, data):
        # type: (str, str) -> Images
        return cls(user_id=user_id, data=data)

    @classmethod
    def fetch(cls, id):
        return cls.query.filter_by(id=id).first()

    def to_dict(self):
        return{
            'id': self.id,
            'user_id': self.user.id,
            'data': self.data
                }



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


if __name__ == "__main__":
    Base.metadata.create_all(db.get_engine(app))
    try:
        from eralchemy import render_er
        render_er(Base, '../er.png')
    except ImportError:
        pass

