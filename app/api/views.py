# coding: utf-8
from . import api
from .. import db
from ..models import Users, Images, Tokens
from flask import request
from ..helpers import secure_jsonify as jsonify
import simplejson as json


def auth(scopes):
    # type: (Union[List(str), str]) -> Union[User, None]
    # TODO: 場合によってエラーを出し分ける
    if isinstance(scopes, basestring):
        scopes = [scopes]

    try:
        header = request.headers.get('Authorization', "")
        token = header.split(' ')[1]
    except Exception:
        return None

    token = Tokens.fetch_by_access_token(token)
    if token is None:
        return None

    users_scopes = set(token.user.scopes)
    if not set(scopes).issubset(users_scopes):
        return None

    return token.user




@api.route('/users', methods=['GET', 'POST'])
def ops_users():
    if request.method == 'GET':
        if not auth('list_user'):
            return jsonify({'error': 'insufficient permission'})

        users = [ i.to_dict() for i in db.session.query(Users).all() ]
        return jsonify({'users': users})

    elif request.method == 'POST':

        data = json.loads(request.data) 
        user_id, user_password = data['user_id'], data['user_password']
        is_restricted = data.get('is_restricted', False) # pylint: disable=no-member
        if is_restricted:
            user = Users.new_user(user_id, user_password)
        else:
            user = Users.new_restricted_user(user_id, user_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'user': user.to_dict()})


@api.route('/images', methods=['GET', 'POST'])
def ops_images():
    if request.method == 'GET':
        if not auth('list_image'):
            return jsonify({'error': 'insufficient permission'})

        images = [i.to_dict() for i in Images.query.all()]
        return jsonify({'images': images})

    elif request.method == 'POST':
        user = auth('add_image')
        if not user:
            return jsonify({'error': 'insufficient permission'})

        data = json.loads(request.data) 
        data = data['data']
        image = user.create_image(data)
        db.session.add(image)
        db.session.commit()
        return jsonify({'image': image.to_dict()})


@api.route('/images/<id>', methods=['GET', 'DELETE'])
def ops_image_by_id(id):
    if request.method == 'GET':
        if not auth('get_image'):
            return jsonify({'error': 'insufficient permission'})
        
        image = Images.fetch(id)
        if not image:
            return jsonify({'error': 'not found image'})
        return jsonify({'image': image.to_dict()})

    elif request.method == 'DELETE':
        user = auth('delete_image')
        if not user:
            return jsonify({'error': 'insufficient permission'})
        
        image = Images.fetch(id)
        if not image:
            return jsonify({'error': 'not found image'})

        if not image.user_id == user.id:
            return jsonify({'error': 'you are NOT images owner'})

        db.session.delete(image) 
        db.session.commit()
        return jsonify({'success': 'deleted'})

