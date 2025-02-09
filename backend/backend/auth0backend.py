import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()
from pymongo import MongoClient
import motor.motor_asyncio

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.DB_NAME]

class Auth0JSONWebTokenAuthentication(BaseAuthentication):
    async def authenticate(self, request):
        auth_header = request.headers.get("Authorization", None)
        print("Auth Header:", auth_header)  # Debugging

        if not auth_header:
            return None

        parts = auth_header.split()

        if parts[0].lower() != "bearer" or len(parts) != 2:
            raise AuthenticationFailed("Invalid Auth0 token header")

        token = parts[1]
        try:
            url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers)
            print("Auth0 Response:", response.status_code, response.text)  # Debugging

            if response.status_code != 200:
                raise AuthenticationFailed("Failed to verify Auth0 token")

            user_info = response.json()
            email = user_info.get("email")

            # Check MongoDB instead of Django ORM
            user_collection = mongo_db["users"]
            existing_user = await user_collection.find_one({"email": email})

            if not existing_user:
                new_user = {
                    "email": email,
                    "nickname": user_info.get("nickname", ""),
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture", ""),
                    "email_verified": user_info.get("email_verified", False),
                }
                await user_collection.insert_one(new_user)

            return (user_info, None)  # Return user_info instead of Django User object
        except Exception as e:
            raise AuthenticationFailed(f"Auth0 token validation failed: {str(e)}")
