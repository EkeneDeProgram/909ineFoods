from rest_framework import serializers
from .models import User#, Address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "last_name", "first_name", "email", "phone_number"]


    # Method to create a new user based on the validated data
    def create(self, validated_data):
        # Create a new CustomUser instance using the create_user method of the CustomUser model
        user = User.objects.create_user(**validated_data)
        # Return the created user
        return user