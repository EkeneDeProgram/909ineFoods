from rest_framework import serializers
from .models import *
from vendors.serializers import MenuItemSerializer
from users.serializers import UserSerializer


# Define serializer for Order
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "status"]


# Define serializer for OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer
    class Meta:
        model = OrderItem
        fields = ["id", "item", "quantity"]


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


# Define serializer for CartItem
class ShoppingCartSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Embed the UserSerializer for the 'user' field

    class Meta:
        model = ShoppingCart
        fields = '__all__'




