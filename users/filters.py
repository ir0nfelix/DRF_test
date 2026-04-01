import django_filters
from django.utils import timezone
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
