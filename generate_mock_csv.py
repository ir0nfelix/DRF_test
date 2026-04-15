import csv
from faker import Faker
import random

fake = Faker('ru_RU')

with open('mock_100_students.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['user_group','username','password','email','first_name','last_name','date_of_birth','phone','tg_name','is_student'])
    for _ in range(100):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = fake.user_name() + str(random.randint(100, 9999))
        password = fake.password(length=12)
        email = fake.ascii_email()
        dob = fake.date_of_birth(minimum_age=17, maximum_age=25).strftime('%Y-%m-%d')
        phone = '8' + ''.join([str(random.randint(0,9)) for _ in range(10)])
        tg_name = '@' + username[:20]
        
        writer.writerow(['', username, password, email, first_name, last_name, dob, phone, tg_name, 'True'])
print("mock_100_students.csv generated")
