from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserAccountSerializer, AuthTokenSerializer


class CreateUserAccountView(generics.CreateAPIView):
    """
    Creates a new user account in the system
    """
    serializer_class = UserAccountSerializer


class CreateTokentView(ObtainAuthToken):
    """
    Creates a new auth token for the user
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
