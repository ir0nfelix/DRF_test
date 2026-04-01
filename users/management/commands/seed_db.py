import random
from django.core.management.base import BaseCommand
from users.models import Student, StudentGroup
from faker import Faker
from mixer.backend.django import mixer

class Command(BaseCommand):
    help = 'Seeds the database with fake data using faker and mixer'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        subjects = ['программирование', 'системное администрирование', 'тестирование', 'дизайн']
        
        # 1. Generate 20 groups
        groups = []
        for _ in range(20):
            subject = random.choice(subjects)
            # Ensure unique group_name
            while True:
                number = f"{random.randint(1, 99):02d}"
                group_name = f"{subject}.{number}"
                if not StudentGroup.objects.filter(group_name=group_name).exists():
                    break
                
            start_year = random.randint(2021, 2026)
            diploma_year = start_year + 4
            
            group = mixer.blend(
                'users.StudentGroup',
                group_name=group_name,
                start_year=start_year,
                diploma_year=diploma_year
            )
            groups.append(group)
            
        self.stdout.write(self.style.SUCCESS('Successfully created 20 groups'))

        # 2. Generate 5-30 students per group
        student_count = 0
        for group in groups:
            num_students = random.randint(5, 30)
            for _ in range(num_students):
                dob = fake.date_of_birth(minimum_age=16, maximum_age=24)
                
                phone = f"8{fake.numerify('##########')}" if random.choice([True, False]) else ""
                tg_name = fake.user_name()[:24] if random.choice([True, False]) else ""
                
                email = fake.unique.email()
                
                gender = random.choice(['M', 'F'])
                if gender == 'M':
                    first_name = fake.first_name_male()
                    last_name = fake.last_name_male()
                else:
                    first_name = fake.first_name_female()
                    last_name = fake.last_name_female()
                    
                username = fake.unique.user_name()
                
                # using mixer for Student
                is_student_flag = (student_count % 5 != 4) # Every 5th student is False
                
                student = mixer.blend(
                    'users.Student',
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_group=group,
                    is_student=is_student_flag,
                    date_of_birth=dob,
                    phone=phone,
                    tg_name=tg_name
                )
                student.set_password('password123')
                student.save()
                
                student_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully created {student_count} students'))
