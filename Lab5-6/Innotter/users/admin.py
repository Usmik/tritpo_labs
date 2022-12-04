from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from users.forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        ('Info', {'fields': ('username', 'email', 'password', 'title', 'role', 'is_blocked')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'user_permissions')})
    )
    add_fieldsets = (
        ('Main info', {'fields': ('username', 'email', 'password1', 'password2')}),
        ('Additional info', {'fields': ('title', 'role', 'is_staff')})
    )
    search_fields = ('username',)
    ordering = ('username', )


admin.site.register(User, CustomUserAdmin)
