from rest_framework import serializers
from .models import User, Address
from vendors.serializers import MenuSerializer

# Define serializer for Address
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "street", "city", "state"]


# Define serializer for User
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
    

# Define serializer for order
# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation['order_date'] = instance.order_date.strftime('%Y-%m-%d %H:%M:%S')
#         return representation
    
# # Define serializer for orderitem
# class OrderItemSerializer(serializers.ModelSerializer):
#     item = MenuItemSerializer()  # Embed MenuItemSerializer for the 'item' field

#     class Meta:
#         model = OrderItem
#         fields = '__all__'

# # Define serializer for status
# class StatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Status
#         fields = '__all__'