import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import cloudinary
import cloudinary.uploader

# --------------------
# App Setup
# --------------------
app = Flask(__name__)
CORS(app)

# --------------------
# Environment Config
# --------------------
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-this")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wallpapers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)

# --------------------
# Cloudinary Config
# --------------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# --------------------
# Constants
# --------------------
ACCOUNT_GUEST = "guest"
ACCOUNT_PERSONAL = "personal"
ACCOUNT_PREMIUM = "premium"

# --------------------
# Models
# --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(20), nullable=False, default=ACCOUNT_GUEST)


class Wallpaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    resolution = db.Column(db.String(20), nullable=False, default="standard")
    is_premium = db.Column(db.Boolean, default=False)
    downloads = db.Column(db.Integer, default=0)

# --------------------
# Routes
# --------------------
@app.route("/")
def home():
    return "PixelHub backend is running 🚀"

# --------------------
# Auth APIs
# --------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400

    if data.get("account_type") not in [ACCOUNT_PERSONAL, ACCOUNT_PREMIUM]:
        account_type = ACCOUNT_PERSONAL
    else:
        account_type = data["account_type"]

    user = User(
        username=data["username"],
        password=generate_password_hash(data["password"]),
        account_type=account_type
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not check_password_hash(user.password, data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)

    return jsonify({"access_token": token}), 200

# --------------------
# Wallpaper APIs
# --------------------
@app.route("/api/pixelhub/wallpapers", methods=["GET"])
@jwt_required(optional=True)
def get_wallpapers():
    user_id = get_jwt_identity()
    account_type = ACCOUNT_GUEST

    if user_id:
        user = User.query.get(user_id)
        account_type = user.account_type

    if account_type == ACCOUNT_GUEST:
        wallpapers = Wallpaper.query.filter_by(is_premium=False).all()
    else:
        wallpapers = Wallpaper.query.all()

    return jsonify([
        {
            "id": w.id,
            "title": w.title,
            "image_url": w.image_url,
            "resolution": w.resolution,
            "is_premium": w.is_premium,
            "downloads": w.downloads
        } for w in wallpapers
    ])


@app.route("/api/pixelhub/wallpapers", methods=["POST"])
@jwt_required()
def add_wallpaper():
    file = request.files.get("image")
    title = request.form.get("title")
    resolution = request.form.get("resolution", "standard")
    is_premium = request.form.get("is_premium", "false").lower() == "true"

    if not file or not title:
        return jsonify({"error": "Title and image required"}), 400

    upload = cloudinary.uploader.upload(
        file,
        folder="pixelhub",
        resource_type="image"
    )

    wallpaper = Wallpaper(
        title=title,
        image_url=upload["secure_url"],
        resolution=resolution,
        is_premium=is_premium
    )

    db.session.add(wallpaper)
    db.session.commit()

    return jsonify({"message": "Wallpaper uploaded"}), 201


@app.route("/api/premium-wallpapers")
@jwt_required()
def premium_wallpapers():
    user = User.query.get(get_jwt_identity())

    if user.account_type != ACCOUNT_PREMIUM:
        return jsonify({"error": "Premium required"}), 403

    wallpapers = Wallpaper.query.all()

    return jsonify([
        {
            "id": w.id,
            "title": w.title,
            "image_url": w.image_url
        } for w in wallpapers
    ])


@app.route("/api/download/<int:wallpaper_id>", methods=["POST"])
def download(wallpaper_id):
    wallpaper = Wallpaper.query.get_or_404(wallpaper_id)
    wallpaper.downloads += 1
    db.session.commit()

    return jsonify({"download_url": wallpaper.image_url})


@app.route("/api/analytics")
@jwt_required()
def analytics():
    user = User.query.get(get_jwt_identity())

    if user.account_type != ACCOUNT_PREMIUM:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify([
        {
            "title": w.title,
            "downloads": w.downloads
        } for w in Wallpaper.query.all()
    ])

# --------------------
# Init & Run
# --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
