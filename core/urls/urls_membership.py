from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.apps.membership.views import MembershipViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"memberships", MembershipViewSet, basename="membership")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
