from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import *
from .serializers import *
from users.utils import *

# Import python standard modules
import jwt, datetime


# Define view for user to create ShoppingCart
class CreateShoppingCartView(APIView):
    
    def post(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Check if a shopping cart already exists for the user
                existing_cart = ShoppingCart.objects.filter(user=user).first()

                if existing_cart:
                    # If a shopping cart already exists, return a message indicating that
                    return Response({"detail": "Shopping cart already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)

                # Create a new shopping cart for the user
                shopping_cart = ShoppingCart.objects.create(user=user)

                # Serialize the shopping cart data
                serializer = ShoppingCartSerializer(shopping_cart)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            

# Define view to enable users add item to thier ShoppingCart
class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Extract data from the request body
                item_id = request.data.get("item")
                quantity = request.data.get("quantity")  

                # Retrieve the item and calculate the price
                item = get_object_or_404(MenuItem, id=item_id)
                price = item.price * quantity

                # Create a new cart item
                cart_item = CartItem.objects.create(
                    cart=user.shoppingcart,  # Assuming the user has a shopping cart associated
                    item=item,
                    quantity=quantity,
                    price=price
                )

                # Serialize the cart item data
                serializer = CartItemSerializer(cart_item)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
    


# Define view to list all items in the users ShoppingCart   
class ShoppingCartItemsView(APIView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Retrieve the user's shopping cart
                shopping_cart = ShoppingCart.objects.filter(user=user).first()

                if shopping_cart:
                    # Retrieve all items in the shopping cart
                    cart_items = CartItem.objects.filter(cart=shopping_cart)
                    serializer = CartItemSerializer(cart_items, many=True)

                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "Shopping cart not found"}, status=status.HTTP_404_NOT_FOUND)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)


# Define a view to delete item from ShoppingCart 
class DeleteCartItemView(APIView):
    def delete(self, request, item_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Retrieve the user's shopping cart
                shopping_cart = ShoppingCart.objects.filter(user=user).first()

                if shopping_cart:
                    # Retrieve the item to be deleted
                    cart_item = CartItem.objects.filter(id=item_id, cart=shopping_cart).first()

                    if cart_item:
                        # Delete the item from the shopping cart
                        cart_item.delete()

                        return Response({"detail": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({"detail": "Item not found in the shopping cart"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"detail": "Shopping cart not found"}, status=status.HTTP_404_NOT_FOUND)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        

# Define a view to enable user update CartItem quantity and price
class UpdateCartItemView(APIView):
    def put(self, request, item_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Retrieve the user's shopping cart
                shopping_cart = ShoppingCart.objects.filter(user=user).first()

                if shopping_cart:
                    # Retrieve the item to be updated
                    cart_item = CartItem.objects.filter(id=item_id, cart=shopping_cart).first()

                    if cart_item:
                        # Update the cart item with the new quantity
                        new_quantity = request.data.get("quantity", cart_item.quantity)
                        cart_item.quantity = new_quantity

                        # Recalculate the price based on the new quantity
                        cart_item.price = cart_item.item.price * new_quantity

                        cart_item.save()

                        # Serialize the updated cart item data
                        serializer = CartItemSerializer(cart_item)

                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"detail": "Item not found in the shopping cart"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"detail": "Shopping cart not found"}, status=status.HTTP_404_NOT_FOUND)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)




