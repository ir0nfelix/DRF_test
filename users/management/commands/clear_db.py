from django.core.management.base import BaseCommand
from users.models import Student, StudentGroup, UserAvatar, UserPicture

class Command(BaseCommand):
    help = 'Clears the database (Student, StudentGroup, UserAvatar, UserPicture)'

    def handle(self, *args, **kwargs):
        from django.db import connection
        with connection.cursor() as cursor:
            # Disable foreign key checks for SQLite
            cursor.execute("PRAGMA foreign_keys = OFF;")
            try:
                # Truncate tables. DELETE FROM is fine for SQLite.
                cursor.execute("DELETE FROM users_useravatar;")
                cursor.execute("DELETE FROM users_userpicture;")
                # Optional: Delete django auth links if needed
                # cursor.execute("DELETE FROM users_student_groups;")
                # cursor.execute("DELETE FROM users_student_user_permissions;")
                cursor.execute("DELETE FROM users_student WHERE is_superuser = 0;")
                cursor.execute("DELETE FROM users_studentgroup;")
            finally:
                cursor.execute("PRAGMA foreign_keys = ON;")
        
        self.stdout.write(self.style.SUCCESS('Successfully cleared database custom tables.'))
