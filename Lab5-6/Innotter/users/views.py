from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer, UserPostSerializer
from users.permissions import IsNotBlocked, AllowedMethod, ObjNotBlockedOrAdmin, IsOwnerOrAdminOrReadOnly
from users.serializers import PagesSerializer
from users.renderers import UserJSONRenderer
from users import viewset_data
from users.services import upload_image_to_s3


class UserViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['$username']

    def get_queryset(self):
        querysets = viewset_data.querysets
        return querysets.get(self.action, User.objects.all())

    def get_permissions(self):
        permissions = viewset_data.permissions
        permissions_for_action = permissions.get(self.action, [IsAuthenticated, IsNotBlocked, AllowedMethod,
                                                               ObjNotBlockedOrAdmin, IsOwnerOrAdminOrReadOnly])
        return [permission() for permission in permissions_for_action]

    def get_serializer_class(self):
        serializers = viewset_data.serializers
        return serializers.get(self.action, UserSerializer)

    @action(detail=False, methods=['post'], renderer_classes=[UserJSONRenderer])
    def register(self, request):
        user = request.data.get('user', {})
        serializer = self.get_serializer(data=user)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], renderer_classes=[UserJSONRenderer])
    def login(self, request):
        user = request.data.get('user', {})
        serializer = self.get_serializer(data=user)
        if serializer.is_valid(raise_exception=False):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'get'], renderer_classes=[UserJSONRenderer])
    def profile(self, request):
        if request.method.lower() == 'get':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer_data = request.data.get('user', {})
        serializer = self.get_serializer(request.user, serializer_data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def block(self, request, pk=None):
        user = self.get_object()
        if not user.is_blocked:
            user.is_blocked = True
            user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def unblock(self, request, pk=None):
        user = self.get_object()
        if user.is_blocked:
            user.is_blocked = False
            user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def pages(self, request, pk=None):
        user = self.get_object()
        serializer = PagesSerializer(instance=user.pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def liked(self, request, pk=None):
        user = self.get_object()
        serializer = UserPostSerializer(instance=user.liked, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def new_page(self, request, pk=None):
        user = self.get_object()
        data = {'owner': user.pk,
                'name': request.data.get('name'),
                'puid': request.data.get('puid')}
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def set_image(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        url = upload_image_to_s3(request=request)
        return Response(data={'url': url}, status=status.HTTP_200_OK)
