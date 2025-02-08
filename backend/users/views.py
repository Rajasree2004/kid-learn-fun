from django.shortcuts import redirect
from django.conf import settings
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

AUTH0_DOMAIN = settings.AUTH0_DOMAIN
AUTH0_CLIENT_ID = settings.AUTH0_CLIENT_ID
AUTH0_CLIENT_SECRET = settings.AUTH0_CLIENT_SECRET

@api_view(["GET"])
def auth0_login(request):
    auth_url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"client_id={AUTH0_CLIENT_ID}&"
        f"response_type=code&"
        f"scope=openid email profile&"  # <-- Ensure "email" scope is included
        f"redirect_uri=http://localhost:8000/api/auth/callback/"
    )
    return redirect(auth_url)

@api_view(["GET"])
def auth0_callback(request):
    code = request.GET.get("code")
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": "http://localhost:8000/api/auth/callback/"
    }

    response = requests.post(token_url, json=payload)
    token_data = response.json()

    if "access_token" not in token_data:
        return JsonResponse({"error": "Auth0 login failed"}, status=400)

    user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    user_info = requests.get(user_info_url, headers=headers).json()

    print("DEBUG: User Info from Auth0:", user_info)  # Log response for debugging

    if "email" not in user_info:
        return JsonResponse({"error": "Email not found in Auth0 response", "data": user_info}, status=400)

    user, _ = User.objects.get_or_create(username=user_info["email"], defaults={"email": user_info["email"]})

    refresh = RefreshToken.for_user(user)
    return JsonResponse({"auth_token": str(refresh.access_token)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    return JsonResponse({"username": request.user.username})
