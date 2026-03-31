
from rest_framework import serializers
from .models import User, TodoList, TodoItem
from django.utils import timezone

#  for the User serializer, we need one for registering and the other for displaying data
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 6)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        
    def create(self,validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'bio', 'profile_picture', 'updated_at']
        read_only_fields = ['id', 'updated_at']

class TodoListSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only = True)
    class Meta:
        model = TodoList
        fields = ['id', 'owner', 'title', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
        
class TodoItemSerializer(serializers.ModelSerializer):
    todo_list = serializers.PrimaryKeyRelatedField(queryset=TodoList.objects.all(),required = False )
    class Meta:
        model = TodoItem
        fields = ['id', 'todo_list', 'title', 'description', 'completed', 'priority', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'todo_list', 'created_at', 'updated_at']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['todo_list'].queryset = TodoList.objects.filter(owner=request.user)
    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value