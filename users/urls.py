from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProtectedStudentViewSet, 
    ProtectedGroupViewSet,
    UserPictureViewSet, 
    UserAvatarViewSet
)

router = DefaultRouter()
router.register(r'protected_users', ProtectedStudentViewSet, basename='protected-users')
router.register(r'protected_groups', ProtectedGroupViewSet, basename='protected-groups')

urlpatterns = [
    path('protected_users/pictures/', UserPictureViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-pictures'),
    path('protected_users/pictures/<int:pk>/', UserPictureViewSet.as_view({
        'delete': 'destroy'
    }), name='user-picture-detail'),

    path('protected_users/avatar/', UserAvatarViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-avatars'),
    path('protected_users/avatar/<int:pk>/', UserAvatarViewSet.as_view({
        'delete': 'destroy'
    }), name='user-avatar-detail'),

    path('', include(router.urls)),
]
