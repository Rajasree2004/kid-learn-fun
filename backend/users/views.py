from django.shortcuts import redirect
from django.conf import settings
import requests
import bcrypt
import jwt
import datetime
from pymongo import MongoClient
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Load MongoDB connection
MONGO_URI = settings.MONGO_URI
mongo_client = MongoClient(MONGO_URI)  # Sync MongoDB connection
mongo_db = mongo_client[settings.DB_NAME]  # Select database
users_collection = mongo_db["users"]

SECRET_KEY = settings.SECRET_KEY  # JWT secret key

AUTH0_DOMAIN = settings.AUTH0_DOMAIN
AUTH0_CLIENT_ID = settings.AUTH0_CLIENT_ID
AUTH0_CLIENT_SECRET = settings.AUTH0_CLIENT_SECRET

# ✅ Password Hashing
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

# ✅ Password Verification
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# ✅ Generate JWT Token Manually (Fix for RefreshToken issue)
def generate_jwt_token(user):
    """ Create a JWT token manually for MongoDB users """
    payload = {
        "email": user["email"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),  # Token expires in 7 days
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# ✅ Register User
@api_view(["POST"])
def register(request):
    """ Register a new user with email & password """
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    # Check if user exists
    if users_collection.find_one({"email": email}):
        return JsonResponse({"error": "User already exists"}, status=400)

    # Hash password before storing
    hashed_password = hash_password(password)

    new_user = {
        "email": email,
        "password": hashed_password,
        "created_at": datetime.datetime.utcnow(),
        "provider": "manual"
    }
    users_collection.insert_one(new_user)

    # ✅ Generate JWT Token
    access_token = generate_jwt_token(new_user)

    return JsonResponse({
        "message": "User registered successfully",
        "access_token": access_token
    })

# ✅ Login User
@api_view(["POST"])
def login(request):
    """ Login user with email & password """
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    # Find user in MongoDB
    user = users_collection.find_one({"email": email})
    if not user:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    # Check password
    if not verify_password(password, user["password"]):
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    # ✅ Generate JWT Token
    access_token = generate_jwt_token(user)

    return JsonResponse({
        "message": "Login successful",
        "access_token": access_token
    })

# ✅ Google Login with Auth0
@api_view(["GET"])
def auth0_login(request):
    """ Redirect user to Auth0 for Google login """
    provider = request.GET.get("provider", "auth0")  # Default to Auth0
    if provider == "google":
        auth_url = (
            f"https://{settings.AUTH0_DOMAIN}/authorize?"
            f"client_id={settings.AUTH0_CLIENT_ID}&"
            f"response_type=code&"
            f"scope=openid email profile&"
            f"connection=google-oauth2&"  # Force Google Login
            f"redirect_uri=http://localhost:8000/api/auth/callback/"
        )
    else:
        auth_url = (
            f"https://{settings.AUTH0_DOMAIN}/authorize?"
            f"client_id={settings.AUTH0_CLIENT_ID}&"
            f"response_type=code&"
            f"scope=openid email profile&"
            f"redirect_uri=http://localhost:8000/api/auth/callback/"
        )

    return redirect(auth_url)

# ✅ Google Login Callback
@api_view(["GET"])
def auth0_callback(request):
    """ Handle Auth0 Google login callback """
    code = request.GET.get("code")
    token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": "http://localhost:8000/api/auth/callback/"
    }

    response = requests.post(token_url, json=payload)
    token_data = response.json()

    if "access_token" not in token_data:
        return JsonResponse({"error": "Auth0 login failed"}, status=400)

    user_info_url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    user_info = requests.get(user_info_url, headers=headers).json()

    if "email" not in user_info:
        return JsonResponse({"error": "Email not found in Auth0 response"}, status=400)

    # Store user in MongoDB
    existing_user = users_collection.find_one({"email": user_info["email"]})

    if not existing_user:
        new_user = {
            "email": user_info["email"],
            "nickname": user_info.get("nickname", ""),
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "email_verified": user_info.get("email_verified", False),
            "provider": "google",
        }
        users_collection.insert_one(new_user)

    return JsonResponse({"message": "User authenticated successfully", "user": user_info})

# ✅ Fetch User Profile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """ Fetch user details from MongoDB """
    email = request.user.email  # Extract email from JWT
    user = users_collection.find_one({"email": email}, {"_id": 0, "password": 0})  # Hide sensitive data
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    return JsonResponse({"user": user})
