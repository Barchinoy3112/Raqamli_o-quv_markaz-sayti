from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TalabaViewSet, KursViewSet, EnrollViewSet

router = DefaultRouter()
router.register(r'talabalar', TalabaViewSet)
router.register(r'kurslar', KursViewSet)
router.register(r'enrolls', EnrollViewSet)

urlpatterns = [
    path('', include(router.urls)),
]