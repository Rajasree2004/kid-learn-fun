import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

# class Auth0JSONWebTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.headers.get("Authorization", None)
#         if not auth_header:
#             return None

#         parts = auth_header.split()

#         if parts[0].lower() != "bearer" or len(parts) != 2:
#             raise AuthenticationFailed("Invalid Auth0 token header")

#         token = parts[1]
#         try:
#             url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
#             headers = {"Authorization": f"Bearer {token}"}
#             response = requests.get(url, headers=headers)

#             if response.status_code != 200:
#                 raise AuthenticationFailed("Failed to verify Auth0 token")

#             user_info = response.json()
#             email = user_info.get("email")

#             user, created = User.objects.get_or_create(username=email, defaults={"email": email})

#             return (user, None)
#         except Exception as e:
#             raise AuthenticationFailed(f"Auth0 token validation failed: {str(e)}")


class Auth0JSONWebTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
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

            user, created = User.objects.get_or_create(username=email, defaults={"email": email})

            return (user, None)
        except Exception as e:
            raise AuthenticationFailed(f"Auth0 token validation failed: {str(e)}")
