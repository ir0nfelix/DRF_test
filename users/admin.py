from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student, StudentGroup

@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name')

@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_group')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_group',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_group',)}),
    )
