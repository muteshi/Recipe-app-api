from django.contrib.auth import get_user_model
from rest_framework import generics, authentication, permissions
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


class ManageUserAccountView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user details
    """
    serializer_class = UserAccountSerializer
    queryset = get_user_model().objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        Retrieve and return authenticated user account
        """
        return self.request.user
