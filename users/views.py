from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Student, StudentGroup
from .serializers import StudentSerializer, GroupSerializer, GroupDetailSerializer
from .filters import StudentGroupFilter

class ProtectedStudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_student', 'user_group']

class ProtectedGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentGroup.objects.annotate(students_count=Count('students')).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = StudentGroupFilter
    ordering_fields = ['group_name', 'students_count', 'start_year', 'diploma_year']
    search_fields = ['group_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupSerializer
        return GroupDetailSerializer

from rest_framework.response import Response
from django.db import transaction
from .models import UserPicture, UserAvatar
from .serializers import UserPictureSerializer, UserAvatarSerializer

class UserPictureViewSet(viewsets.ModelViewSet):
    serializer_class = UserPictureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPicture.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"user_photos": serializer.data})

class UserAvatarViewSet(viewsets.ModelViewSet):
    serializer_class = UserAvatarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAvatar.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            UserAvatar.objects.filter(user=self.request.user, is_active=True).update(is_active=False)
            serializer.save(user=self.request.user, is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"user_avatars": serializer.data})

    def perform_destroy(self, instance):
        user = instance.user
        was_active = instance.is_active
        
        with transaction.atomic():
            instance.delete()
            if was_active:
                latest_avatar = UserAvatar.objects.filter(user=user).order_by('-created_at').first()
                if latest_avatar:
                    latest_avatar.is_active = True
                    latest_avatar.save()
