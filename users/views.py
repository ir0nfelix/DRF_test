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
