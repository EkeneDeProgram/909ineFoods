from rest_framework import serializers
from .models import *
from vendors.serializers import MenuItemSerializer
from users.serializers import UserSerializer




# Define serializer for OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer
    class Meta:
        model = OrderItem
        # fields = ["id", "item", "quantity"]
        fields = '__all__'


# Define serializer for Status
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "name"]


# Define serializer for CartItem
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'






