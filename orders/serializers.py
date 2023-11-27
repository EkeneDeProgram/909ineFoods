from rest_framework import serializers
from .models import *
from vendors.serializers import MenuSerializer
from users.serializers import UserSerializer



# Define serializer for OrderItem
class OrderSerializer(serializers.ModelSerializer):
    item = MenuSerializer
    class Meta:
        model = Order
        fields = '__all__'


# Define serializer for Status
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "name"]


# Define serializer for CartItem
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'






