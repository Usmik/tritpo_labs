from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from django.utils import timezone

from posts.models import Post
from posts.serializers import PostSerializer
from users.permissions import IsNotBlocked
from posts.permissions import PostOwnerIsNotBlockedOrStaff, PostPageIsNotBlockedOrStaff,\
    PageIsNotPrivate, IsOwnerOrStaff, IsNotPostMethod
from posts import viewset_data


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotBlocked, IsNotPostMethod, IsOwnerOrStaff | PageIsNotPrivate]
    retrieve_view_fields = ('id', 'content', 'reply_to', 'created_at', 'updated_at', 'page__id', 'page__name',
                            'page__is_private', 'page__unblock_date', 'page__owner__id',
                            'page__owner__is_blocked')

    def get_permissions(self):
        permissions = viewset_data.permissions
        permissions_for_action = self.permission_classes + permissions.get(self.action, [PostPageIsNotBlockedOrStaff,
                                                                                         PostOwnerIsNotBlockedOrStaff])
        return [permission() for permission in permissions_for_action]

    def get_serializer_class(self):
        serializers = viewset_data.serializers
        return serializers.get(self.action, PostSerializer)

    def get_queryset(self):
        querysets = viewset_data.querysets
        return querysets.get(self.action, Post.objects.select_related('page', 'page__owner', 'reply_to')
                                                      .only(*self.retrieve_view_fields).prefetch_related('likes').all())

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(instance=post.likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.user not in tuple(post.likes.all()):
            post.likes.add(request.user)
        serializer = self.get_serializer(instance=post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        if request.user in tuple(post.likes.all()):
            post.likes.remove(request.user)
        serializer = self.get_serializer(instance=post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def news(self, request):
        query = self.get_queryset().filter(Q(page__owner__id__in=request.user.follows.all())
                                           | Q(page__owner__id=request.user.pk))\
                                    .filter(Q(page__unblock_date=None)
                                        | Q(page__unblock_date__lt=datetime.now(tz=timezone.utc)))\
                                    .filter(page__owner__is_blocked=False)
        serializer = self.get_serializer(instance=query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        query = self.get_queryset().filter(reply_to=pk).filter(Q(page__unblock_date=None)
                                    | Q(page__unblock_date__lt=datetime.now(tz=timezone.utc)))\
                                    .filter(page__owner__is_blocked=False)
        serializer = self.get_serializer(instance=query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
