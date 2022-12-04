from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.permissions import IsNotBlocked, IsAdmin, IsOwner, IsImage
from users.serializers import RegistrationSerializer, LoginSerializer, MyUserSerializer, NewPageSerializer
from users.serializers import UserPostSerializer, UserImageSerializer

querysets = {
            'pages': User.objects.prefetch_related('pages').all(),
            'liked': User.objects.prefetch_related('liked').all(),
        }

permissions = {
            'register': [AllowAny],
            'login': [AllowAny],
            'profile': [IsAuthenticated, IsNotBlocked],
            'block': [IsAuthenticated, IsAdmin, IsNotBlocked],
            'unblock': [IsAuthenticated, IsAdmin, IsNotBlocked],
            'pages': [IsAuthenticated, IsNotBlocked],
            'liked': [IsAuthenticated, IsNotBlocked],
            'new_page': [IsAuthenticated, IsNotBlocked, IsOwner],
            'set_image': [IsAuthenticated, IsNotBlocked, IsOwner, IsImage],
        }

serializers = {
         'register': RegistrationSerializer,
         'login': LoginSerializer,
         'profile': MyUserSerializer,
         'liked': UserPostSerializer,
         'new_page': NewPageSerializer,
         'set_image': UserImageSerializer,
        }
