from rest_framework import serializers
from django.contrib.auth import authenticate

from pages.models import Page
from users.models import User
from posts.models import Post
from Innotter.settings import AWS
from Innotter.aws import s3_client


class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'title', 'role', 'is_blocked', 'image_url')
        read_only_fields = ('is_blocked', 'role', 'email', 'username', 'image_url')

    def get_image_url(self, obj):
        if obj.image_s3_path:
            return s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': AWS['AWS_BUCKET_NAME'],
                                                            'Key': obj.image_s3_path},
                                                    ExpiresIn=3600)


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'content', 'created_at')


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'puid')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'token')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'token')

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        self.username_validation(username)
        self.password_validation(password)

        user = authenticate(username=username, password=password)

        self.user_validation(user)

        return {
            'username': user.username,
            'token': user.token
        }

    def username_validation(self, username):
        if username is None:
            raise serializers.ValidationError('Username is required')

    def password_validation(self, password):
        if password is None:
            raise serializers.ValidationError('Password is required')

    def user_validation(self, user):
        if user is None:
            raise serializers.ValidationError('User not founded')
        if not user.is_active:
            raise serializers.ValidationError('User was deactivated')


class MyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'token')
        read_only_fields = ('token', 'id')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserImageSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class NewPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'puid', 'owner')
