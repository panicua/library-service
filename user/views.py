from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView, TokenObtainPairView

from user.serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Create a new user",
        description="Endpoint to create a new user.",
        responses={201: UserSerializer}
    )
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve the authenticated user",
        description="Retrieve the details of the currently authenticated user.",
        responses={200: UserSerializer}
    ),
    put=extend_schema(
        summary="Update the authenticated user",
        description="Update the details of the currently authenticated user.",
        responses={200: UserSerializer}
    ),
    patch=extend_schema(
        summary="Partially update the authenticated user",
        description="Partially update the details of the currently authenticated user.",
        responses={200: UserSerializer}
    )
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
