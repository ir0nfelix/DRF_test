import django_filters
from django.utils import timezone
from django.db.models import Q
from .models import StudentGroup, Student

class StudentGroupFilter(django_filters.FilterSet):
    group_name = django_filters.CharFilter(lookup_expr='icontains')
    is_archive = django_filters.BooleanFilter(method='filter_is_archive')
    
    # Aliased field for diploma_year
    stop_year = django_filters.NumberFilter(field_name='diploma_year', lookup_expr='exact')
    stop_year__gt = django_filters.NumberFilter(field_name='diploma_year', lookup_expr='gt')
    stop_year__gte = django_filters.NumberFilter(field_name='diploma_year', lookup_expr='gte')
    stop_year__lt = django_filters.NumberFilter(field_name='diploma_year', lookup_expr='lt')
    stop_year__lte = django_filters.NumberFilter(field_name='diploma_year', lookup_expr='lte')
    
    # Aliased field for annotated count
    count = django_filters.NumberFilter(field_name='students_count', lookup_expr='exact')
    count__gt = django_filters.NumberFilter(field_name='students_count', lookup_expr='gt')
    count__gte = django_filters.NumberFilter(field_name='students_count', lookup_expr='gte')
    count__lt = django_filters.NumberFilter(field_name='students_count', lookup_expr='lt')
    count__lte = django_filters.NumberFilter(field_name='students_count', lookup_expr='lte')

    class Meta:
        model = StudentGroup
        fields = {
            'start_year': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }

    def filter_is_archive(self, queryset, name, value):
        current_year = timezone.now().year
        if value is True:
            return queryset.filter(diploma_year__lt=current_year)
        elif value is False:
            return queryset.filter(diploma_year__gte=current_year)
        return queryset

class StudentFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    group_name = django_filters.CharFilter(field_name='user_group__group_name', lookup_expr='icontains')
    
    is_currently_study = django_filters.BooleanFilter(method='filter_is_currently_study')
    has_contacts = django_filters.BooleanFilter(method='filter_has_contacts')

    class Meta:
        model = Student
        fields = {
            'date_of_birth': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'is_student': ['exact'],
            'user_group': ['exact'],
        }

    def filter_is_currently_study(self, queryset, name, value):
        current_year = timezone.now().year
        q_studying = Q(is_student=True) & (Q(user_group__isnull=True) | Q(user_group__diploma_year__gte=current_year))
        if value is True:
            return queryset.filter(q_studying)
        elif value is False:
            return queryset.exclude(q_studying)
        return queryset

    def filter_has_contacts(self, queryset, name, value):
        q_contacts = (Q(phone__isnull=False) & ~Q(phone='')) | (Q(tg_name__isnull=False) & ~Q(tg_name=''))
        if value is True:
            return queryset.filter(q_contacts)
        elif value is False:
            return queryset.exclude(q_contacts)
        return queryset

