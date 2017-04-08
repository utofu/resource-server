from . import api
from .. import db
from ..models import Users, Images
from flask import request
from ..helpers import secure_jsonify as jsonify
import simplejson as json


@api.route('/users', methods=['GET', 'POST'])
def ops_users():
    if request.method == 'GET':
        users = [ i.to_dict() for i in db.session.query(Users).all() ]
        return jsonify({'users': users})

    elif request.method == 'POST':
        data = json.loads(request.data) 
        user_id, user_password = data['user_id'], data['user_password']
        try:
            is_restricted = data['is_restricted']
        except KeyError:
            is_restricted = False

        if is_restricted:
            user = Users.new_user(user_id, user_password)
        else:
            user = Users.new_restricted_user(user_id, user_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'user': user.to_dict()})


@api.route('/images', methods=['GET', 'POST'])
def ops_images():
    return 'poe'

@api.route('/images/:id', methods=['GET', 'DELETE', 'UPDATE'])
def ops_image_by_id(user_id):
    return 'poe'
