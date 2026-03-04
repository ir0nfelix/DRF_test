from django.core.management.base import BaseCommand
from users.models import Student, StudentGroup

class Command(BaseCommand):
    help = 'Setup initial development data'

    def handle(self, *args, **kwargs):
        # Create group
        group, created = StudentGroup.objects.get_or_create(group_name='backend-1')
        
        # Create standard student
        if not Student.objects.filter(username='student').exists():
            student = Student.objects.create_user(
                username='student',
                password='student',
                user_group=group
            )
            self.stdout.write(self.style.SUCCESS(f"Created student user: {student.username}"))
        else:
            self.stdout.write(self.style.WARNING("User 'student' already exists"))

        # Create superuser
        if not Student.objects.filter(username='admin').exists():
            admin = Student.objects.create_superuser(
                username='admin',
                password='students2026',
                email='admin@example.com',
                user_group=group
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin.username}"))
        else:
            self.stdout.write(self.style.WARNING("User 'admin' already exists"))
        
        self.stdout.write(self.style.SUCCESS("Initial data setup complete!"))
