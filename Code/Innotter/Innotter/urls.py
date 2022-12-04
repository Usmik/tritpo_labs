import debug_toolbar
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from pages.views import PageViewSet
from users.views import UserViewSet
from posts.views import PostViewSet
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


router = routers.DefaultRouter()
router.register(r'pages', PageViewSet, basename='pages')
router.register(r'users', UserViewSet, basename='users')
router.register(r'posts', PostViewSet, basename='posts')

schema_view = get_schema_view(  # new
    openapi.Info(
        title="Innotter API",
        default_version='v1',
        description="Created by Usmik",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('swagger-ui/',
         TemplateView.as_view(
            template_name='swaggerui/swaggerui.html',
            extra_context={'schema_url': 'openapi-schema'}
         ),
         name='swagger-ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('__debug__/', include(debug_toolbar.urls))
]
