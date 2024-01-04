"""
core URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from home_app import views as home_app_views

urlpatterns = [
    path("admin/", admin.site.urls),
]

router = routers.DefaultRouter()
router.register(r"register", home_app_views.RegisterViewSet, basename="register")

# Wire up our API using automatic URL routing.
urlpatterns += [
    path("api/v1/", include((router.urls, "apiv1"), namespace="apiv1")),
    path(
        "api/v1/login/",
        home_app_views.RFQOSTObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/v1/logout/",
        home_app_views.RFQOSTokenBlacklistView.as_view(),
        name="token_blacklist",
    ),
    path(
        "api/v1/token/refresh/",
        home_app_views.RFQOSTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/v1/token/verify/",
        home_app_views.RFQOSTokenVerifyView.as_view(),
        name="token_refresh",
    ),
]
