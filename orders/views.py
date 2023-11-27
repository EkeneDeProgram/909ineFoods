# Import third party modules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


# Import project modules
from .models import *
from .serializers import *
from users.utils import *

# Import python standard modules
import jwt


# Define view to enable users add item to thier Cart
class AddToCartView(APIView):
   def post(self, request, item_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                item = get_object_or_404(Menu, id=item_id)

                # Check if the item is already in the user's cart
                cart_item, created = Cart.objects.get_or_create(user=user, item=item)
                if not created:
                    # If the item already exists, increment the quantity by one
                    cart_item.quantity += 1
                    cart_item.save()

                serializer = CartSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
    



# Define a view to enable user update CartItem quantity 
class UpdateCartItemView(APIView):
    def put(self, request, item_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = get_object_or_404(User, id=user_id)

                cart_item = get_object_or_404(Cart, user=user, item=item_id)

                # Update the quantity based on the request data
                new_quantity = request.data.get('quantity', cart_item.quantity)
                cart_item.quantity = new_quantity
                cart_item.save()

                serializer = CartSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            except Cart.DoesNotExist:
                return Response({"detail": "CartItem not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



# Define view to list all user cartitem 
class ListCartItemsView(APIView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user_cart_items = Cart.objects.filter(user_id=user_id)
                serializer = CartSerializer(user_cart_items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
 


# Define a view to delete an item from user Cart 
class DeleteCartItemView(APIView):
    def delete(self, request, item_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                # Ensure that the user only deletes items from their own cart
                cart_item = get_object_or_404(Cart, user_id=user_id, item_id=item_id)
                cart_item.delete()

                return Response({"detail": "Item deleted successfully"}, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
    


# Define view to enable user delete all user cartitem
class DeleteAllCartItemsView(APIView):
    def delete(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                # Ensure that the user only deletes items from their own cart
                cart_items = Cart.objects.filter(user_id=user_id)
                cart_items.delete()

                return Response({"detail": "All items deleted successfully"}, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)


# Define view to enable user place order
class AddCartItemsToOrderView(APIView):
    def post(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Ensure that the user only adds items from their own cart to OrderItem
                cart_items = Cart.objects.filter(user_id=user_id)
                order_items = []

                # Create OrderItem instances from CartItem instances
                for cart_item in cart_items:
                    order_items.append(
                        Order(
                            user=user,
                            item=cart_item.item,
                            quantity=cart_item.quantity,
                            # price=cart_item.item.price * cart_item.quantity,
                            price=cart_item.item.price,
                            order_date=timezone.now(),
                            delivered=False,
                            paid_for=False  # Adjust this based on your logic
                        )
                    )

                # Bulk create the OrderItem instances
                Order.objects.bulk_create(order_items)

                # Delete the cart items after creating the order items
                cart_items.delete()

                return Response({"detail": "Cart items added to OrderItem successfully"}, status=status.HTTP_201_CREATED)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



# Define view for user to retrieve a list of orders placed
class ListOrdersView(APIView):
    def get(self, request, *args, **kwargs):
       jwt_token = request.COOKIES.get("jwt")

       if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Get orders for the authenticated user
                orders = Order.objects.filter(user=user)

                # Serialize the orders
                serializer = OrderSerializer(orders, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

       return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



# Define view for user to retrieve a list of orders placed with a specific food vendor.
class VendorOrdersView(APIView):
    def get(self, request, vendor_id, *args, **kwargs):
        
        jwt_token = request.COOKIES.get("jwt")
        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Get orders for the authenticated user and a specific vendor
                orders = Order.objects.filter(user=user, item__vendor__id=vendor_id)

                # Serialize the orders using OrderItemSerializer
                serializer = OrderSerializer(orders, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



# Define view for user to retrieve details about a specific order.
class OrderDetailsView(APIView):
    def get(self, request, order_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Get the order for the authenticated user
                order = get_object_or_404(Order, id=order_id, user=user)

                # Serialize the order details
                serializer = OrderSerializer(order)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)


# Define view to enable user update order(quantity)
class UpdateOrderView(APIView):
    def put(self, request, order_id,  *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                user = User.objects.get(id=user_id)

                # Get the order for the authenticated user
                order = get_object_or_404(Order, id=order_id, user=user)


                # Update the quantity based on the request data
                new_quantity = request.data.get('quantity', order.quantity)
                order.quantity = new_quantity
                order.save()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)



# Define view to enable user Cancels a specific order.



