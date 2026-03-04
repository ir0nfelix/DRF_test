from rest_framework import serializers
from .models import Student, StudentGroup

class StudentSerializer(serializers.ModelSerializer):
    # Read-only field to show group_name in student response
    group_name = serializers.CharField(source='user_group.group_name', read_only=True)
    
    class Meta:
        model = Student
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_group', 'group_name')

class GroupSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = ('id', 'group_name', 'count')

    def get_count(self, obj):
        return obj.students.count()

class GroupDetailSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentGroup
        fields = ('id', 'group_name', 'students')
