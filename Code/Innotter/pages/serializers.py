from rest_framework import serializers

from pages.models import Page, Tag
from posts.models import Post
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class PageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_blocked')


class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('page', 'id', 'content', 'reply_to', 'created_at')


class PageSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'puid', 'tags', 'is_private')
        read_only_fields = ('is_private',)


class PageRetrieveSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)
    owner = PageUserSerializer(many=False, read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'puid', 'tags', 'description', 'owner', 'is_private', 'unblock_date')
        read_only_fields = ('is_private', 'unblock_date')


class SimplePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'unblock_date')
