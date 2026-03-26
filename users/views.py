from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Student, StudentGroup
from .serializers import StudentSerializer, GroupSerializer, GroupDetailSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]

class ProtectedStudentViewSet(StudentViewSet):
    permission_classes = [IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = StudentGroup.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupSerializer
        return GroupDetailSerializer

class ProtectedGroupViewSet(GroupViewSet):
    permission_classes = [IsAuthenticated]

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
