#python -m venv venv
#venv\Scripts\activate
#pip install flask flask-sqlalchemy flask-jwt-extended pyotp qrcode bcrypt pymysql pillow
#.\venv\Scripts\python.exe  (Windows)

from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import pyotp
import qrcode
import io
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database Configuration

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    secret_key = db.Column(db.String(32), nullable=False)

# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Create tables (Run once)
with app.app_context():
    db.create_all()

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    secret_key = pyotp.random_base32()

    new_user = User(username=username, password=hashed_password, secret_key=secret_key)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Generate QR Code for Google Authenticator
@app.route('/generate_qr/<username>', methods=['GET'])
def generate_qr(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    otp_uri = pyotp.totp.TOTP(user.secret_key).provisioning_uri(username, issuer_name="FlaskApp")
    
    img = qrcode.make(otp_uri)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

# Verify 2FA Code
@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    data = request.json
    username = data.get('username')
    otp_code = data.get('otp')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    totp = pyotp.TOTP(user.secret_key)
    if not totp.verify(otp_code):
        return jsonify({"message": "Invalid 2FA code"}), 401

    return jsonify({"message": "2FA Verified"}), 200

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": "Enter 2FA code", "username": username}), 200

# Generate JWT Token after 2FA
@app.route('/generate_token', methods=['POST'])
def generate_token():
    data = request.json
    username = data.get('username')
    otp_code = data.get('otp')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    totp = pyotp.TOTP(user.secret_key)
    if not totp.verify(otp_code):
        return jsonify({"message": "Invalid 2FA code"}), 401

    access_token = create_access_token(identity=username, expires_delta=False)
    return jsonify(access_token=access_token), 200

# CRUD Operations on Products
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.json
    new_product = Product(name=data.get('name'), price=data.get('price'))
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "price": p.price} for p in products]), 200

@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    data = request.json
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    db.session.commit()
    return jsonify({"message": "Product updated"}), 200

@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
