from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from users.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'title', 'role', 'is_staff']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'title', 'role', 'is_staff', 'is_superuser', 'is_blocked']
