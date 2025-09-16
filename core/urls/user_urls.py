from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.apps.users.views import UserViewSet,TrainerMemberViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"trainer-members", TrainerMemberViewSet, basename="trainermember")

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
