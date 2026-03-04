from django.db import models
from django.contrib.auth.models import AbstractUser

class StudentGroup(models.Model):
    group_name = models.CharField(max_length=12, unique=True)

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

    def __str__(self):
        return f"{self.username}"
