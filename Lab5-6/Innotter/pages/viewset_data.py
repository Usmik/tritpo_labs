from pages.models import Page
from pages.permissions import IsStaff, ObjUserNotBlocked, IsPageNotBlocked, IsOwner, \
    IsNotFollowerAndNotOwner, NotInFollowRequests, IsFollowerAndNotOwner, \
    InFollowRequests, IsPrivatePage, RequestIdInFollowRequests, IsValidTag, AllowedMethod
from pages.serializers import PageSerializer, PostsSerializer,\
    PageUserSerializer, SimplePageSerializer

permissions = {
            'list': [AllowedMethod],
            'create': [AllowedMethod],
            'destroy': [AllowedMethod],
            'retrieve': [IsStaff | ObjUserNotBlocked, IsStaff | IsPageNotBlocked],
            'follow': [ObjUserNotBlocked, IsPageNotBlocked, IsNotFollowerAndNotOwner, NotInFollowRequests],
            'unfollow': [ObjUserNotBlocked, IsPageNotBlocked, IsFollowerAndNotOwner, InFollowRequests],
            'followers': [ObjUserNotBlocked | IsStaff, IsPageNotBlocked | IsStaff],
            'posts': [ObjUserNotBlocked | IsStaff, IsPageNotBlocked | IsStaff],
            'set_unblock_date': [IsStaff],
            'accept_all_requests': [IsPageNotBlocked, IsOwner, IsPrivatePage],
            'decline_all_requests': [IsPageNotBlocked, IsOwner, IsPrivatePage],
            'accept_request': [IsPageNotBlocked, IsOwner, IsPrivatePage, RequestIdInFollowRequests],
            'decline_request': [IsPageNotBlocked, IsOwner, IsPrivatePage, RequestIdInFollowRequests],
            'tag': [IsPageNotBlocked, IsOwner, IsValidTag],
}

serializers = {
            'list': PageSerializer,
            'followers': PageUserSerializer,
            'posts': PostsSerializer,
            'set_unblock_date': SimplePageSerializer,
            'follow_requests': PageUserSerializer,
        }

querysets = {
            'list': Page.objects.prefetch_related('tags').all(),
            'follow': Page.objects.select_related('owner')
                                  .prefetch_related('followers', 'follow_requests', 'tags').all(),
            'unfollow': Page.objects.select_related('owner')
                                    .prefetch_related('followers', 'follow_requests', 'tags').all(),
            'followers': Page.objects.select_related('owner')
                                     .prefetch_related('followers').all(),
            'posts': Page.objects.select_related('owner')
                                 .prefetch_related('posts').all(),
            'follow_requests': Page.objects.select_related('owner')
                                           .prefetch_related('follow_requests').all(),
            'accept_all_requests': Page.objects.select_related('owner')
                                               .prefetch_related('followers', 'follow_requests', 'tags').all(),
            'decline_all_requests': Page.objects.select_related('owner')
                                        .prefetch_related('follow_requests', 'tags').all(),
            'accept_request': Page.objects.select_related('owner')
                                          .prefetch_related('followers', 'follow_requests', 'tags').all(),
            'decline_request': Page.objects.select_related('owner')
                                           .prefetch_related('follow_requests', 'tags').all(),
            'new_post': Page.objects.select_related('owner')
                                           .prefetch_related('followers', 'tags').all(),
}
