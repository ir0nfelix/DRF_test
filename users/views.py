from rest_framework import viewsets, filters    
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
import xlwt
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Student, StudentGroup
from .serializers import StudentSerializer, GroupSerializer, GroupDetailSerializer
from .filters import StudentGroupFilter, StudentFilter

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProtectedStudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = StudentFilter
    search_fields = ['first_name', 'last_name', 'user_group__group_name']
    ordering_fields = ['first_name', 'last_name', 'date_of_birth', 'user_group__group_name']
    pagination_class = StandardResultsPagination

    @action(detail=False, methods=['get'])
    def csv_report(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_report.csv"'
        response.write(u'\ufeff'.encode('utf8'))  # BOM for Excel
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Логин', 'Имя', 'Фамилия', 'Учебная группа', 'Дата рождения', 'Способ связи', 'Обучается в данный момент'])
        
        for student in queryset:
            group_name = student.user_group.group_name if getattr(student, 'user_group', None) else ''
            
            # Format Date
            dob_str = student.date_of_birth.strftime('%d.%m.%Y') if getattr(student, 'date_of_birth', None) else ''
            
            # Format Contacts
            contacts = []
            if getattr(student, 'email', ''):
                contacts.append(f"Email: {student.email}")
            if getattr(student, 'phone', ''):
                contacts.append(f"Тел: {student.phone}")
            if getattr(student, 'tg_name', ''):
                contacts.append(f"TG: {student.tg_name}")
            contact_str = "\n".join(contacts)
            
            # Is Active
            is_active_str = 'Да' if getattr(student, 'is_currently_study', False) else 'Нет'
            
            writer.writerow([
                student.username, 
                student.first_name, 
                student.last_name, 
                group_name, 
                dob_str,
                contact_str,
                is_active_str
            ])
        return response

    @action(detail=False, methods=['get'])
    def xls_report(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="students_report.xls"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Студенты')
        
        # Header formatting
        header_style = xlwt.XFStyle()
        header_style.font.bold = True
        
        # Wrapped text cell style
        wrap_style = xlwt.XFStyle()
        wrap_style.alignment.wrap = 1
        
        columns = ['Логин', 'Имя', 'Фамилия', 'Учебная группа', 'Дата рождения', 'Способ связи', 'Обучается в данный момент']
        for col_num, column_title in enumerate(columns):
            ws.write(0, col_num, column_title, header_style)
            
        for row_num, student in enumerate(queryset, start=1):
            group_name = student.user_group.group_name if getattr(student, 'user_group', None) else ''
            
            # Format Date
            dob_str = student.date_of_birth.strftime('%d.%m.%Y') if getattr(student, 'date_of_birth', None) else ''
            
            # Format Contacts
            contacts = []
            if getattr(student, 'email', ''):
                contacts.append(f"Email: {student.email}")
            if getattr(student, 'phone', ''):
                contacts.append(f"Тел: {student.phone}")
            if getattr(student, 'tg_name', ''):
                contacts.append(f"TG: {student.tg_name}")
            contact_str = "\n".join(contacts)
            
            # Is Active
            is_active_str = 'Да' if getattr(student, 'is_currently_study', False) else 'Нет'
            
            ws.write(row_num, 0, student.username, wrap_style)
            ws.write(row_num, 1, student.first_name, wrap_style)
            ws.write(row_num, 2, student.last_name, wrap_style)
            ws.write(row_num, 3, group_name, wrap_style)
            ws.write(row_num, 4, dob_str, wrap_style)
            ws.write(row_num, 5, contact_str, wrap_style)
            ws.write(row_num, 6, is_active_str, wrap_style)
            
        wb.save(response)
        return response

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
