from rest_framework import viewsets, mixins, permissions, generics

from .models import User
from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class UpdateDestroyRetrieveUserViewSet(mixins.UpdateModelMixin, 
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin, 
                              viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer