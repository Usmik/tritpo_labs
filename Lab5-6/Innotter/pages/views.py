from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pages.models import Page, Tag
from pages.permissions import IsPageNotBlocked, IsOwner
from pages.serializers import PageRetrieveSerializer, PostsSerializer
from users.permissions import IsNotBlocked
from users.models import User
from pages import viewset_data
from pages.tasks import send_mail_to_followers
from Innotter.producer import Statistics
import requests


class PageViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ['$name', '$puid', 'tags__name']
    permission_classes = [IsAuthenticated, IsNotBlocked]

    def get_permissions(self):
        permissions = viewset_data.permissions
        permissions_for_action = self.permission_classes + permissions.get(self.action, [IsPageNotBlocked, IsOwner])
        return [permission() for permission in permissions_for_action]

    def get_serializer_class(self):
        serializers = viewset_data.serializers
        return serializers.get(self.action, PageRetrieveSerializer)

    def get_queryset(self):
        querysets = viewset_data.querysets
        return querysets.get(self.action, Page.objects.select_related('owner').prefetch_related('tags').all())

    @action(detail=True, methods=['patch'])
    def follow(self, request, pk=None):
        page = self.get_object()
        if not page.is_private:
            page.followers.add(request.user)
        else:
            page.follow_requests.add(request.user)
        serializer = PageRetrieveSerializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def unfollow(self, request, pk=None):
        page = self.get_object()
        if not page.is_private:
            page.followers.remove(request.user)
        else:
            page.follow_requests.remove(request.user)
        serializer = PageRetrieveSerializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        page = self.get_object()
        serializer = self.get_serializer(instance=page.followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        page = self.get_object()
        serializer = self.get_serializer(instance=page.posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def new_post(self, request, pk=None):
        page = self.get_object()
        data = {'page': pk,
                'content': request.data.get('content'),
                'reply_to': request.data.get('reply_to')}
        serializer = PostsSerializer(data=data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            followers_mails = [follower.email for follower in page.followers.all()]
            send_mail_to_followers.delay(data['content'], page.name, followers_mails)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def set_unblock_date(self, request, pk=None):
        page = self.get_object()
        page.unblock_date = request.data.get('unblock_date')
        serializer = self.get_serializer(data={'unblock_date': request.data.get('unblock_date')})
        if serializer.is_valid(raise_exception=False):
            page.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def private(self, request, pk=None):
        page = self.get_object()
        if not page.is_private:
            page.is_private = True
            page.save()
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def public(self, request, pk=None):
        page = self.get_object()
        if page.is_private:
            for user in page.follow_requests.all():
                page.followers.add(user)
                page.follow_requests.remove(user)
            page.is_private = False
            page.save()
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def follow_requests(self, request, pk=None):
        page = self.get_object()
        serializer = self.get_serializer(instance=page.follow_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def accept_all_requests(self, request, pk=None):
        page = self.get_object()
        for user in page.follow_requests.all():
            page.followers.add(user)
            page.follow_requests.remove(user)
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def decline_all_requests(self, request, pk=None):
        page = self.get_object()
        for user in page.follow_requests.all():
            page.follow_requests.remove(user)
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='accept_request/(?P<request_pk>[^/.]+)')
    def accept_request(self, request, pk=None, request_pk=None):
        page = self.get_object()
        user_to_accept = User.objects.get(pk=request_pk)
        page.follow_requests.remove(user_to_accept)
        page.followers.add(user_to_accept)
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['patch'], url_path='decline_request/(?P<request_pk>[^/.]+)')
    def decline_request(self, request, pk=None, request_pk=None):
        page = self.get_object()
        user_to_decline = User.objects.get(pk=request_pk)
        page.follow_requests.remove(user_to_decline)
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post', 'delete'])
    def tag(self, request, pk=None):
        page = self.get_object()
        tag_name = request.data.get('name')
        tag = Tag.objects.get_or_create(name=tag_name)[0]
        if request.method.lower() == 'post' and tag not in tuple(page.tags.all()):
            page.tags.add(tag.id)
        elif request.method.lower() == 'delete' and tag in tuple(page.tags.all()):
            page.tags.remove(tag.id)
        serializer = self.get_serializer(instance=page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        page = self.get_object()
        return Response(data={'stats': Statistics().get_stats(page_pk=int(page.pk))}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def rest_stats(self, request, pk=None):
        page = self.get_object()
        response = requests.get('http://microservice:8001/stats/1/')
        return Response(data={'stats': response.json()}, status=status.HTTP_200_OK)
