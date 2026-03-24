
from rest_framework import serializers
from .models import User

#  for the User serializer, we need one for registering and the other for displaying data
class RegisterSerializer(serializers.ModelSerializers):
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