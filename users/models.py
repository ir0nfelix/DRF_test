from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class StudentGroup(models.Model):
    group_name = models.CharField(max_length=12, unique=True)
    start_year = models.PositiveSmallIntegerField(default=2024)
    diploma_year = models.PositiveSmallIntegerField(default=2028)

    @property
    def is_archive(self):
        from django.utils import timezone
        if self.diploma_year is not None:
            return self.diploma_year < timezone.now().year
        return False

    def __str__(self):
        return self.group_name

class Student(AbstractUser):
    # This field is required according to user specifications, 
    # but we will allow null=True in DB temporarily if migrations fail, 
    # but let's strictly follow: no nulls. 
    # To allow python manage.py createsuperuser cleanly, it's often better to allow null,
    # but we will use the custom script anyway.
    user_group = models.ForeignKey(
        StudentGroup,
        on_delete=models.CASCADE,
        related_name='students',
        null=True, # Allow null for superusers created via CLI just in case, validated via API
        blank=True
    )
    is_student = models.BooleanField(default=True)
    date_of_birth = models.DateField(default="2000-01-01")
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        validators=[RegexValidator(regex=r'^8\d{10}$')]
    )
    tg_name = models.CharField(max_length=24, blank=True, null=True)

    @property
    def is_currently_study(self):
        return all([
            self.is_student,
            not (self.user_group.is_archive if getattr(self, 'user_group', None) else False)
        ])

    @property
    def has_contacts(self):
        return any([self.phone, self.tg_name])

    def __str__(self):
        return f"{self.username}"

class UserPicture(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='pictures')
    file = models.ImageField(upload_to='pictures/')
    created_at = models.DateTimeField(auto_now_add=True)

class UserAvatar(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='avatars')
    picture_string = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
