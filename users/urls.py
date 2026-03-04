from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, ProtectedStudentViewSet, GroupViewSet, ProtectedGroupViewSet

router = DefaultRouter()
router.register(r'users', StudentViewSet, basename='users')
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'protected_users', ProtectedStudentViewSet, basename='protected-users')
router.register(r'protected_groups', ProtectedGroupViewSet, basename='protected-groups')

urlpatterns = [
    path('', include(router.urls)),
]
