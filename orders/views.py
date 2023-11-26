from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import *
from .serializers import *
from users.utils import *

# Import python standard modules
import jwt, datetime


# Define view to enable users add item to thier Cart
class AddToCartView(APIView):
   def post(self, request, item_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                item = get_object_or_404(MenuItem, id=item_id)

                # Check if the item is already in the user's cart
                cart_item, created = CartItem.objects.get_or_create(user=user, item=item)
                if not created:
                    # If the item already exists, increment the quantity by one
                    cart_item.quantity += 1
                    cart_item.save()

                serializer = CartItemSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
    


# Define view to list all items in the users ShoppingCart   

# Define a view to delete item from ShoppingCart 


# # Define a view to enable user update CartItem quantity and price

# Define view to enable user place order
