from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from users.admin import CustomUserAdmin
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import User


class AdminTestCase(TestCase):
    def test_forms(self):
        test_admin = CustomUserAdmin(model=User, admin_site=AdminSite)
        self.assertEqual(test_admin.form, CustomUserChangeForm)
        self.assertEqual(test_admin.add_form, CustomUserCreationForm)

    def test_fieldsets(self):
        test_admin = CustomUserAdmin(model=User, admin_site=AdminSite)
        expected_add_fieldsets = [{'email', 'username', 'password1', 'password2'}, {'is_staff', 'role', 'title'}]
        self.assertEqual(expected_add_fieldsets[0], set(test_admin.add_fieldsets[0][1].get('fields')))
        self.assertEqual(expected_add_fieldsets[1], set(test_admin.add_fieldsets[1][1].get('fields')))

    def test_search_fields_and_ordering(self):
        test_admin = CustomUserAdmin(model=User, admin_site=AdminSite)
        self.assertEqual(test_admin.search_fields, ('username',))
        self.assertEqual(test_admin.ordering, ('username',))
