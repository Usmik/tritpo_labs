import jwt
from rest_framework import authentication, exceptions

from Innotter import settings
from users.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        request.user = None
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()
        if not auth_header or len(auth_header) != 2:
            return None
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')
        if prefix.lower() != auth_header_prefix:
            return None
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        payload = self._payload_validation(token)
        user = self._user_validation(payload)
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User was deactivated')
        return user, token

    def _payload_validation(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except Exception:
            raise exceptions.AuthenticationFailed('Token decode failed.')
        return payload

    def _user_validation(self, payload):
        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        return user
