from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenVerifyView,
    TokenRefreshView,
)
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tasks', views.TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh')
]