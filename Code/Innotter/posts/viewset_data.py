from posts.models import Post
from posts.permissions import PostOwnerIsNotBlockedOrStaff, PostPageIsNotBlockedOrStaff, IsOwner,\
    IsOwnerOrStaff
from posts.serializers import PostRetrieveSerializer, PostUserSerializer

list_view_fields = ('id', 'content', 'reply_to', 'created_at', 'page__id', 'page__name',
                    'page__is_private', 'page__unblock_date', 'page__owner__id', 'page__owner__is_blocked')

permissions = {
            'list': [],
            'update': [PostPageIsNotBlockedOrStaff, PostOwnerIsNotBlockedOrStaff, IsOwner],
            'partial_update': [PostPageIsNotBlockedOrStaff, PostOwnerIsNotBlockedOrStaff, IsOwner],
            'destroy': [PostPageIsNotBlockedOrStaff, IsOwnerOrStaff],
        }

serializers = {
            'retrieve': PostRetrieveSerializer,
            'likes': PostUserSerializer,
            'like': PostRetrieveSerializer,
            'unlike': PostRetrieveSerializer,
        }

querysets = {
            'list': Post.objects.select_related('page', 'reply_to').only(*list_view_fields).all(),
            'likes': Post.objects.select_related('page', 'page__owner').prefetch_related('likes').all(),
            'news': Post.objects.select_related('page', 'page__owner', 'reply_to')
                                .only(*list_view_fields).prefetch_related('likes').all(),
            'replies': Post.objects.select_related('page', 'reply_to', 'page__owner').only(*list_view_fields).all(),
        }
