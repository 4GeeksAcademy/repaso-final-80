"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, Users, Books
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


@api.route('/test', methods=['GET'])
def test():
    return jsonify({"msg": "OK"}), 200

#CRUD ---> CREATE READ UPDATE DELETE ---> POST GET PUT DELETE

@api.route('/register', methods=['POST'])
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return jsonify({"msg": 'todos los datos son necesarios'}), 400
    
    exists = Users.query.filter_by(email=email).first()
    if exists:
        return jsonify({"msg": 'el correo ya existe!'})
    
    hashed_password = generate_password_hash(password)
    new_user = Users(
        email=email,
        password=hashed_password,
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()
    token = create_access_token(identity=str(new_user.id))
    return jsonify({"msg": 'woo-hoo', "token": token}), 201

    
@api.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email or not password:
        return jsonify({"msg": 'todos los datos son necesarios'}), 400
    
    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": 'el correo no existe!'}), 404
    
    if not check_password_hash(user.password, password):
        return jsonify({"msg": 'el correo/contrasena estan mal!'}), 400
    token = create_access_token(identity=str(user.id))
    return jsonify({"msg": 'woo-hoo', "token": token}), 200


@api.route('/books', methods=['GET'])
def all_books():
    data = Books.query.all() # devuelve lista
    data = [book.serialize() for book in data]
    return jsonify({"msg": 'OK', "payload": data})

@api.route('/books/<int:id>', methods=['GET'])
def one_book(id):
    data = Books.query.get(id) # devuelve UN objeto
    return jsonify({"msg": 'OK', "payload": data.serialize()})

@api.route('/books', methods=['POST'])
def create_book():
    title = request.json.get('title', None)
    author_id = request.json.get('author_id', None)

    if not title or not author_id:
        return jsonify({"msg": "missing data"})
    new_book = Books(
        title=title,
        author_id = author_id
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"msg": "book created", 'payload': new_book.serialize()})


@api.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    data = Books.query.get(id) # devuelve UN objeto
    db.session.delete(data)
    db.session.commit()
    return jsonify({"msg": 'OK', "payload": 'book deleted'})


@api.route('/books/<int:id>', methods=['PUT'])
def upd_book(id):
    title = request.json.get('title', None)
    author_id = request.json.get('author_id', None)

    data = Books.query.get(id) # devuelve UN objeto
    if not data:
        return jsonify({"msg": "no book"})
    data.title = title or data.title
    data.author_id = author_id or data.author_id
    db.session.commit()
    return jsonify({"msg": "book updated", 'payload': data.serialize()})


@api.route('/user_info', methods=['GET'])
@jwt_required()
def get_user_info():
    id = get_jwt_identity()
    user = Users.query.get(id)

    return jsonify({"msg": "OK", "payload": user.serialize()})