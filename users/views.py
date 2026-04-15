from rest_framework import viewsets, filters, mixins    
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db.models import Count
import csv
import xlwt
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Student, StudentGroup
from .serializers import StudentSerializer, GroupSerializer, GroupDetailSerializer
from .filters import StudentGroupFilter, StudentFilter
from .permissions import IsSuperUser

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProtectedStudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.prefetch_related('avatars', 'pictures').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = StudentFilter
    search_fields = ['first_name', 'last_name', 'user_group__group_name']
    ordering_fields = ['first_name', 'last_name', 'date_of_birth', 'user_group__group_name']
    pagination_class = StandardResultsPagination

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            from .serializers import StudentCreateSerializer
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            from .serializers import StudentUpdateSerializer
            return StudentUpdateSerializer
        from .serializers import StudentSerializer
        return StudentSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsSuperUser])
    def import_students(self, request):
        if 'file' not in request.FILES and 'csv' not in request.FILES:
            return Response({"error": "No file uploaded. Please upload a CSV using 'file' or 'csv' key in form-data."}, status=400)
            
        file = request.FILES.get('file') or request.FILES.get('csv')
        
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
        except UnicodeDecodeError:
            return Response({"error": "Invalid encoding. Ensure the file is UTF-8 encoded."}, status=400)
            
        import csv
        reader = csv.reader(decoded_file, delimiter=';')
        
        try:
            next(reader)
        except StopIteration:
            return Response({"error": "File is empty"}, status=400)
            
        students_data = []
        for row_idx, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                continue
                
            if len(row) < 4:
                return Response({"error": f"Row {row_idx} is malformed. Expected at least 4 columns (group, username, password, email)."}, status=400)
                
            student = {
                'user_group': row[0].strip() if len(row) > 0 and row[0].strip() else None,
                'username': row[1].strip() if len(row) > 1 else '',
                'password': row[2].strip() if len(row) > 2 else '',
                'email': row[3].strip() if len(row) > 3 else '',
            }
            
            if len(row) > 4 and row[4].strip(): student['first_name'] = row[4].strip()
            if len(row) > 5 and row[5].strip(): student['last_name'] = row[5].strip()
            if len(row) > 6 and row[6].strip(): student['date_of_birth'] = row[6].strip()
            if len(row) > 7 and row[7].strip(): student['phone'] = row[7].strip()
            if len(row) > 8 and row[8].strip(): student['tg_name'] = row[8].strip()
            
            if len(row) > 9 and row[9].strip():
                val = row[9].strip().lower()
                student['is_student'] = val in ['true', '1', 'yes', 't']
                
            students_data.append(student)
            
        if not students_data:
            return Response({"error": "No valid data rows found in CSV"}, status=400)
            
        from django.db import transaction
        from .serializers import StudentCreateSerializer
        
        try:
            with transaction.atomic():
                serializer = StudentCreateSerializer(data=students_data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "message": f"Successfully imported {len(students_data)} students.",
                        "imported_count": len(students_data)
                    }, status=201)
                else:
                    return Response({
                        "error": "Validation failed during import.",
                        "details": serializer.errors
                    }, status=400)
        except Exception as e:
            return Response({"error": f"Import failed due to server error: {str(e)}"}, status=500)

    @action(detail=False, methods=['get'])
    def csv_report(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_report.csv"'
        response.write(u'\ufeff'.encode('utf8'))  # BOM for Excel
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Логин', 'Имя', 'Фамилия', 'Учебная группа', 'Дата рождения', 'Способ связи', 'Обучается в данный момент', 'Есть аватарка', 'Есть фото'])
        
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
                is_active_str,
                'Да' if student.has_avatar else 'Нет',
                'Да' if student.has_pictures else 'Нет'
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
        
        columns = ['Логин', 'Имя', 'Фамилия', 'Учебная группа', 'Дата рождения', 'Способ связи', 'Обучается в данный момент', 'Есть аватарка', 'Есть фото']
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
            ws.write(row_num, 7, 'Да' if student.has_avatar else 'Нет', wrap_style)
            ws.write(row_num, 8, 'Да' if student.has_pictures else 'Нет', wrap_style)
            
        wb.save(response)
        return response

class ProtectedGroupViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = StudentGroup.objects.annotate(students_count=Count('students')).all()
    
    def get_permissions(self):
        if self.action not in ['list', 'retrieve']:
            return [IsSuperUser()]
        return [IsAuthenticated()]

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
