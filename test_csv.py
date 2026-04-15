import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from users.models import Student, StudentGroup

Student.objects.filter(username__in=['ivan_ivanov', 'maria_s', 'vasya_pupkin', 'adminG']).delete()
StudentGroup.objects.get_or_create(id=1, defaults={'group_name':'testG1', 'start_year':2024, 'diploma_year':2028})
StudentGroup.objects.get_or_create(id=2, defaults={'group_name':'testG2', 'start_year':2024, 'diploma_year':2028})

admin = Student(username='adminG', is_superuser=True, email='admin@example.com')
admin.set_password('pass')
admin.save()

client = APIClient()
client.force_authenticate(user=admin)

with open('students_import_sample.csv', 'rb') as f:
    response = client.post('/api/v1/protected_users/import_students/', {'file': f}, format='multipart')

print("STATUS:", response.status_code)
print("DATA:", response.data)
