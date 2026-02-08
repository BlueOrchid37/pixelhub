from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import cloudinary
import cloudinary.uploader
from werkzeug.security import generate_password_hash, check_password_hash


cloudinary.config(
    cloud_name="dux2q4ejf",
    api_key="962568541917317",
    api_secret="qtOEvsg2_jeYNxANNr_ylLy2ML4",
    secure=True
)


app = Flask(__name__)
CORS(app)

from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# --------------------
# Database Config
# --------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wallpapers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------
# Models
# --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)


class Wallpaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    resolution = db.Column(db.String(20), nullable=False)  # standard / 4k
    is_premium = db.Column(db.Boolean, default=False)
    downloads = db.Column(db.Integer, default=0)


# --------------------
# Routes
# --------------------

@app.route("/")
def home():
    return "Wallpaper backend is running!"

# --------------------
# USER APIs
# --------------------




# --------------------
# WALLPAPER APIs
# --------------------

@app.route("/api/pixelhub/wallpapers", methods=["GET"])
def get_wallpapers():
    account_type = request.args.get("account", "guest")

    if account_type == "guest":
        wallpapers = Wallpaper.query.filter_by(is_premium=False).all()
    else:
        wallpapers = Wallpaper.query.all()

    result = []
    for w in wallpapers:
        result.append({
            "id": w.id,
            "title": w.title,
            "image_url": w.image_url,
            "resolution": w.resolution,
            "is_premium": w.is_premium
        })

    return jsonify(result)


@app.route("/api/pixelhub/wallpapers", methods=["POST"])
@jwt_required()
def add_wallpaper():
    file = request.files.get("image")
    title = request.form.get("title")
    is_premium = request.form.get("is_premium", "false") == "true"

    if not file or not title:
        return jsonify({"error": "Title and image required"}), 400

    upload = cloudinary.uploader.upload(file)

    wallpaper = Wallpaper(
        title=title,
        image_url=upload["secure_url"],
        is_premium=is_premium
    )

    db.session.add(wallpaper)
    db.session.commit()

    return jsonify({"message": "Wallpaper uploaded"}), 201


@app.route("/api/upload", methods=["POST"])
def upload_wallpaper():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    result = cloudinary.uploader.upload(
        file,
        folder="pixelhub"
    )

    return jsonify({
        "image_url": result["secure_url"]
    }), 201

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    hashed_pw = generate_password_hash(data["password"])

    user = User(
        username=data["username"],
        password=hashed_pw,
        account_type=data["account_type"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity={
        "id": user.id,
        "account_type": user.account_type
    })

    return jsonify({"access_token": token})

@app.route("/api/premium-wallpapers")
@jwt_required()
def premium_wallpapers():
    user = get_jwt_identity()

    if user["account_type"] != "personal":
        return jsonify({"error": "Upgrade required"}), 403

    wallpapers = Wallpaper.query.all()
    return jsonify([...])

@app.route("/api/download/<int:id>", methods=["POST"])
def download(id):
    wallpaper = Wallpaper.query.get(id)

    wallpaper.download_count += 1
    db.session.commit()

    return jsonify({
        "download_url": wallpaper.image_url
    })

@app.route("/api/analytics")
def analytics():
    wallpapers = Wallpaper.query.all()

    return jsonify([
        {
            "title": w.title,
            "downloads": w.download_count
        }
        for w in wallpapers
    ])



# --------------------
# Init DB & Run
# --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
