from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.apps.diet.views import (
    NutritionPlanViewSet,
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"nutrition-plans", NutritionPlanViewSet, basename="nutritionplan")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
