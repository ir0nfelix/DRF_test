import base64
import binascii
import os
from rest_framework import serializers
from .models import Student, StudentGroup, UserPicture, UserAvatar

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
        if value.size > 3 * 1024 * 1024:
            raise serializers.ValidationError("File size must be under 3 MB.")
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

class StudentSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='user_group.group_name', read_only=True)
    is_currently_study = serializers.ReadOnlyField()
    has_avatar = serializers.ReadOnlyField()
    has_pictures = serializers.ReadOnlyField()
    contacts = serializers.SerializerMethodField()
    photos = UserPictureSerializer(source='pictures', many=True, read_only=True)
    avatars = UserAvatarSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'username', 'first_name', 'last_name', 'user_group', 'group_name', 'date_of_birth', 'is_currently_study', 'has_avatar', 'has_pictures', 'contacts', 'photos', 'avatars', 'is_student')
        extra_kwargs = {
            'username': {'read_only': True}
        }
        
    def get_contacts(self, obj):
        return {
            "email": obj.email,
            "phone": obj.phone,
            "tg_name": obj.tg_name
        }

class StudentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.RegexField(regex=r'^8\d{10}$', required=False, write_only=True, allow_blank=True, allow_null=True)
    tg_name = serializers.CharField(max_length=24, required=False, write_only=True, allow_blank=True, allow_null=True)

    class Meta:
        model = Student
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'user_group', 'date_of_birth', 'phone', 'tg_name', 'is_student')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        tg_name = validated_data.pop('tg_name', None)
        password = validated_data.pop('password')
        
        user = Student(**validated_data)
        user.set_password(password)
        if phone is not None:
            user.phone = phone
        if tg_name is not None:
            user.tg_name = tg_name
        user.save()
        return user

class StudentUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.RegexField(regex=r'^8\d{10}$', required=False, write_only=True, allow_blank=True, allow_null=True)
    tg_name = serializers.CharField(max_length=24, required=False, write_only=True, allow_blank=True, allow_null=True)

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'user_group', 'date_of_birth', 'phone', 'tg_name', 'is_student')

    def update(self, instance, validated_data):
        if 'phone' in validated_data:
            instance.phone = validated_data.pop('phone')
        if 'tg_name' in validated_data:
            instance.tg_name = validated_data.pop('tg_name')
        return super().update(instance, validated_data)

class GroupSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    is_archive = serializers.ReadOnlyField()
    start_year = serializers.IntegerField(required=True)
    diploma_year = serializers.IntegerField(required=True)

    class Meta:
        model = StudentGroup
        fields = ('id', 'group_name', 'count', 'is_archive', 'start_year', 'diploma_year')

    def validate(self, data):
        start_year = data.get('start_year')
        diploma_year = data.get('diploma_year')
        if start_year is not None and diploma_year is not None:
            if start_year > diploma_year:
                raise serializers.ValidationError({"start_year": "start_year не может быть больше diploma_year"})
        return data

    def get_count(self, obj):
        return obj.students.count()

class GroupDetailSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)
    is_archive = serializers.ReadOnlyField()

    class Meta:
        model = StudentGroup
        fields = ('id', 'group_name', 'is_archive', 'start_year', 'diploma_year', 'students')
