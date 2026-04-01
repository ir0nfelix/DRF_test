from rest_framework import serializers
from .models import Student, StudentGroup

class StudentSerializer(serializers.ModelSerializer):
    # Read-only field to show group_name in student response
    group_name = serializers.CharField(source='user_group.group_name', read_only=True)
    is_currently_study = serializers.ReadOnlyField()
    contacts = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_group', 'group_name', 'date_of_birth', 'is_currently_study', 'contacts')

    def get_contacts(self, obj):
        return {
            "phone": obj.phone,
            "tg_name": obj.tg_name
        }

class GroupSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    is_archive = serializers.ReadOnlyField()

    class Meta:
        model = StudentGroup
        fields = ('id', 'group_name', 'count', 'is_archive', 'start_year', 'diploma_year')

    def get_count(self, obj):
        return obj.students.count()

class GroupDetailSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)
    is_archive = serializers.ReadOnlyField()

    class Meta:
        model = StudentGroup
        fields = ('id', 'group_name', 'is_archive', 'start_year', 'diploma_year', 'students')

import base64
import binascii
import os
from .models import UserPicture, UserAvatar

class UserPictureSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='file.url', read_only=True)
    mime = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = UserPicture
        fields = ('id', 'url', 'mime', 'size', 'file')
        extra_kwargs = {
            'file': {'write_only': True}
        }

    def validate_file(self, value):
        # 3 MB limit
        if value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError("File size must be under 3 MB.")
        
        # Valid extensions: jpeg, jpg, png
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.jpeg', '.jpg', '.png']:
            raise serializers.ValidationError("File format must be JPEG, JPG, or PNG.")
        return value

    def get_mime(self, obj):
        try:
            ext = os.path.splitext(obj.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                return 'jpg'
            elif ext == '.png':
                return 'png'
            return 'unknown'
        except Exception:
            return 'unknown'

    def get_size(self, obj):
        try:
            size_bytes = obj.file.size
            if size_bytes >= 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f}M".replace('.0M', 'M')
            elif size_bytes >= 1024:
                return f"{size_bytes / 1024:.0f}K"
            return f"{size_bytes}B"
        except Exception:
            return "0B"

class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        fields = ('id', 'picture_string', 'is_active')
        read_only_fields = ('is_active',)

    def validate_picture_string(self, value):
        try:
            if value.startswith('data:image'):
                base64_data = value.split(',')[1]
            else:
                base64_data = value
            decoded = base64.b64decode(base64_data, validate=True)
            if len(decoded) > 512 * 1024:
                raise serializers.ValidationError("Image size must be under 512 KB.")
        except (binascii.Error, IndexError, ValueError):
            raise serializers.ValidationError("Invalid base64 string.")
        return value
