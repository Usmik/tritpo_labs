from django.db.models.functions.datetime import datetime
from rest_framework import serializers

from posts.models import Post
from pages.models import Page
from users.models import User


class PostPagesSerializer(serializers.ModelSerializer):
    is_blocked = serializers.SerializerMethodField()

    def get_is_blocked(self, obj):
        if obj.unblock_date is None:
            return obj.owner.is_blocked
        return obj.unblock_date > datetime.now(obj.unblock_date.tzinfo)

    class Meta:
        model = Page
        fields = ('id', 'name', 'is_private', 'is_blocked')


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'content', 'created_at', 'page')


class PostUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class PostSerializer(serializers.ModelSerializer):
    page = PostPagesSerializer(read_only=True, many=False)
    reply_to = ReplySerializer(read_only=True, many=False)

    class Meta:
        model = Post
        fields = ('id', 'content', 'reply_to', 'created_at', 'page')


class PostRetrieveSerializer(PostSerializer):
    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Post
        fields = ('id', 'content', 'reply_to', 'created_at', 'updated_at', 'page', 'likes_count')
