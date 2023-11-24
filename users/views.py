# Import third party modules
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

# Import python standard modules
import jwt, datetime

# Import project modules
from .serializers import *
from .models import User, Address
from .utils import *
from vendors.models import *
from vendors.serializers import *


# Define view to create/register user
class RegistrationView(CreateAPIView):
    serializer_class = UserSerializer # Specify the serializer class

    # Define method that handles the POST request for user registration.
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) # Create an instance of the UserSerializer class
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)

            verification_code = generate_verification_code() # Generate verification code for user
            hash_verification_code = hash_VC(verification_code) # Hash verification code

            # Update and save user details
            user.hashed_verification_code = hash_verification_code 
            user.save()

            # Send email verification code 
            email = user.email
            send_verification_email(email, verification_code)

            # Serialize the user data, including the 'id' field
            serialized_data = UserSerializer(user).data

            return Response(serialized_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Define a login view
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the user's input email from the request
        email = request.data.get("email") 

        # Check if the email exists in the database
        user = get_user_model().objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        verification_code = generate_verification_code() # Generate verification code for user
        hash_verification_code = hash_VC(verification_code) # Hash verification code

         # Update and save user details
        user.hashed_verification_code = hash_verification_code 
        user.save()

        # Send email verification code 
        email = user.email
        send_verification_email(email, verification_code)

        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        

# Define view to verify user verification code and generate JWT
class VerifyCodeView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the user's input verification code from the request
        user_input_code = request.data.get("verification_code") 

        try:
            hashed_input_code = hash_VC(user_input_code) # Hash user inputed verification code
            user = User.objects.get(hashed_verification_code=hashed_input_code) # Get user with that email

            # If user Exists
            if user: 
                user.is_verified = True
                user.is_login = True
                user.save()

                # Create a payload dictionary containing information to be encoded in the JWT
                payload = {
                    "id": user.id,
                    "iat": datetime.datetime.utcnow()
                }

                # Encode the payload into a JWT using the specified secret key and algorithm
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITH).decode("utf-8")

                # Return token via cookies
                reponse = Response()
                reponse.set_cookie(key="jwt", value=token, httponly=True)
                reponse.data = {
                    "jwt": token
                }

            return reponse
        except User.DoesNotExist:
            return Response({"detail": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        

# Define view to retrieve user information(Profile) based on a JWT stored in the request's cookies
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        # Check if the token is not present
        if not token:
            # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
             # Decode the JWT using the provided secret key and algorithm
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.DecodeError:
            # Handle every potential decoding errors.
            raise AuthenticationFailed("Unauthenticated!")
        
        user = User.objects.filter(id=payload["id"]).first()
        serializer = UserSerializer(user)
        address_serializer = AddressSerializer(user.address)
        response_data = {
            "user": serializer.data,
            "address": address_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
       

# Define view to logout user by deleting the JWT cookie
class LogoutView(APIView):
    def post(self, request):
        # Get the JWT token from the cookie
        token = request.COOKIES.get("jwt")

        # Check if the token is not present
        if not token:
           # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            # Decode the JWT using the provided secret key and algorithm
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.DecodeError:
            # Handle every potential decoding errors.
            return Response({"detail": "An error occurred"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user
        user = get_user_model().objects.filter(id=payload["id"]).first()

        # Check if the user is found
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Update is_login to False
        user.is_login = False
        user.save()

        # Delete the 'jwt' cookie from the response
        response = Response()
        # Delete the 'jwt' cookie from the response. 
        response.delete_cookie("jwt")
        response.data = {
            "message": "Logout successful"
        }
        return response
    

# Define view to update user email
class UpdateEmailView(APIView):
    def put(self, request, *args, **kwargs):
        # Get the JWT token from the cookie
        token = request.COOKIES.get("jwt")

        # Get the new email from user
        new_email = request.data.get("email")

        # Check if the token is not present
        if not token:
           # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            # Decode the JWT using the provided secret key and algorithm
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.DecodeError:
            # Handle every potential decoding errors.
            return Response({"detail": "An error occurred"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user
        user = get_user_model().objects.filter(id=payload["id"]).first()

        # Check if the user is found
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the new email already exists in the database
        if get_user_model().objects.exclude(id=user.id).filter(email=new_email).exists():
            return Response({"detail": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        verification_code = generate_verification_code() # Generate verification code for user
        hash_verification_code = hash_VC(verification_code) # Hash verification code
        
        # Update user details
        user.email = new_email
        user.username = new_email
        user.hashed_verification_code = hash_verification_code
        user.save()

        # Send email verification code 
        new_email = user.email
        send_verification_email(new_email, verification_code)
        return Response({"message": "Email updated successfully"}, status=status.HTTP_200_OK)
    

# Define view to update user phone number
class UpdatePhoneNumberView(APIView):
   def put(self, request, *args, **kwargs):
        # Get the JWT token from the cookie
        token = request.COOKIES.get("jwt")

        # Get the new email from user
        new_phone_number = request.data.get("phone_number")

        # Check if the token is not present
        if not token:
           # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            # Decode the JWT using the provided secret key and algorithm
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.DecodeError:
            # Handle every potential decoding errors.
            return Response({"detail": "An error occurred"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user
        user = get_user_model().objects.filter(id=payload["id"]).first()

        # Check if the user is found
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the new phone number exists in the database
        if get_user_model().objects.exclude(id=user.id).filter(phone_number=new_phone_number).exists():
            return Response({"detail": "phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update user details
        user.phone_number = new_phone_number
        user.save()

        return Response({"message": "phone number updated successfully"}, status=status.HTTP_200_OK)
   

# Define view to update user first_name and last_name
class UpdateUserNameView(APIView):
    def put(self, request, *args, **kwargs):
        # Get the JWT token from the cookie
        token = request.COOKIES.get("jwt")

        # Get the new name from user
        new_first_name = request.data.get("first_name")
        new_last_name = request.data.get("last_name")

        # Check if the token is not present
        if not token:
           # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            # Decode the JWT using the provided secret key and algorithm
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.DecodeError:
            # Handle every potential decoding errors.
            return Response({"detail": "An error occurred"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user
        user = get_user_model().objects.filter(id=payload["id"]).first()

        # Check if the user is found
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Update user details
        if new_first_name:
            user.first_name = new_first_name
        if new_last_name:
                user.last_name = new_last_name

        user.save()
        return Response({"message": "Name updated successfully"}, status=status.HTTP_200_OK)
    

# Define View to update user address
class UpdateUserAddressView(APIView):
    def put(self, request, *args, **kwargs):
        # Get the JWT token from the cookie
        token = request.COOKIES.get("jwt")

        # Get the new address details from the request
        new_street = request.data.get("street")
        new_city = request.data.get("city")
        new_state = request.data.get("state")

        # Check if the token is not present
        if not token:
            # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            # Decode the JWT using the provided secret key and algorithm
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.DecodeError:
            # Handle every potential decoding errors.
            return Response({"detail": "An error occurred"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user
        user = get_user_model().objects.filter(id=payload["id"]).first()

        # Check if the user is found
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        # Check if the user has an associated address
        if user.address:
            # Update only the specified address fields
            if new_street:
                user.address.street = new_street
            if new_city:
                user.address.city = new_city
            if new_state:
                user.address.state = new_state

            user.address.save()
        else:
            # If the user does not have an associated address, create one
            address = Address.objects.create(street=new_street, city=new_city, state=new_state)
            user.address = address
            user.save()

        # Serialize the updated user and address details
        serializer = UserSerializer(user)
        address_serializer = AddressSerializer(user.address)
        response_data = {
            "message": "Address updated successfully",
            "user": serializer.data,
            "address": address_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

# Define view to resend verification code to user
class ResendVerificationCodeView(UpdateAPIView):
    def update(self, request, *args, **kwargs):
        # Get the user based on the provided email
        email = request.data.get("email")
        user = get_user_model().objects.filter(email=email).first()

        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already verified
        if user.is_verified:
            return Response({"detail": "User is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate and save a new verification code
        verification_code = generate_verification_code()
        hash_verification_code = hash_VC(verification_code)
        user.hashed_verification_code = hash_verification_code
        user.save()

        # Send the new verification code via email
        send_verification_email(email, verification_code)

        return Response({"message": "Verification code resent successfully"}, status=status.HTTP_200_OK)
    


# Define view to update user profile image
class UpdateUserImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def patch(self, request, *args, **kwargs):
        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        # Get the image from the request
        image = request.data.get("profile_image")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
            

                if not image:
                    return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
                
                user = User.objects.get(id=user_id)
                
                # Update the vendor's image
                user.profile_image = image
                user.save()
                response.data = {
                    "message": "update successfull"
                }
                    
            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return response
            

# Define view to enable user delete thier account
class UserDeleteAccountView(APIView):
    def delete(self, request, *args, **kwargs):
        response = Response()

        jwt_token = request.COOKIES.get("jwt")
        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                user_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                user = User.objects.get(id=user_id)

                # Delete the vendor
                user.delete()
                response.data = {
                    "message": "Your account has been deleted successfully"
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response

  
# Define view to list all active vendors
class ListActiveVendorsView(APIView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])

                active_vendors = Vendor.objects.filter(is_active=True, is_login=True)
                serializer = VendorSerializer(active_vendors, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            

# Allows users to retrieve details about a specific vendor based on the vendor ID. 
class VendorDetailsView(APIView):
    def get(self, request, vendor_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])

                # Retrieve the vendor instance or return a 404 response if not found
                vendor = get_object_or_404(Vendor, id=vendor_id)
                serializer = VendorSerializer(vendor)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
       

# Define view to enables users to view the menu of a specific food vendor
class VendorMenuView(APIView):
    def get(self, request, vendor_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                
                # Retrieve the vendor instance or return a 404 response if not found
                vendor = get_object_or_404(Vendor, id=vendor_id)
                
                # Retrieve all items added to the menu by the vendor
                menu_items = MenuItem.objects.filter(vendor=vendor)

                # Serialize the items and return the data
                serializer = MenuItemSerializer(menu_items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            

# Define a view that provides users with a list of food categories.
class CategoryListView(APIView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])

                # Retrieve all food categories
                categories = Category.objects.all()

                # Serialize the categories and return the data
                serializer = CategorySerializer(categories, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Define a view to retrieve a list of vendors offering food in a specific category 
class VendorsByCategoryView(APIView):
    def get(self, request, category_id, *args, **kwargs):  
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH]) 

                # Retrieve the category instance or return a 404 response if not found
                category = get_object_or_404(Category, id=category_id)
            
                # Retrieve all vendors offering food in the specified category
                vendors = Vendor.objects.filter(menuitem__category=category).distinct()

                # Serialize the vendors and return the data
                serializer = VendorSerializer(vendors, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Define a view to enable user place with a specific vendor
# class PlaceOrderView(APIView):
#     def post(self, request, vendor_id, *args, **kwargs):

#         jwt_token = request.COOKIES.get("jwt")
#         vendor = get_object_or_404(Vendor, id=vendor_id)

#         # Extract order data from the request
#         order_data = request.data.get("order", {})
#         items_data = request.data.get("items", [])

#         if jwt_token:
#                 try:
#                     decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH]) 
#                     user_id = decoded_payload.get("id")
#                     user = User.objects.get(id=user_id)

#                     # Calculate the total price based on items' prices and quantities
#                     total_price = sum(
#                         MenuItem.objects.get(id=item_data["item"]).price * item_data["quantity"]
#                         for item_data in items_data
#                     )

#                     # Create a new order with the calculated total price
#                     order_serializer = OrderSerializer(
#                         data={**order_data, "user": user.id, "vendor": vendor.id, "total_price": total_price}
#                     )

#                     if order_serializer.is_valid():
#                         order = order_serializer.save()

#                         # Create order items
#                         for item_data in items_data:
#                             item_serializer = OrderItemSerializer(data={**item_data, "order": order.id})
#                             if item_serializer.is_valid():
#                                 item_serializer.save()
#                             else:
#                                 # If item data is invalid, delete the order and return an error response
#                                 order.delete()
#                                 return Response({"detail": "Invalid order item data"}, status=status.HTTP_400_BAD_REQUEST)
#                         return Response({"detail": "Order placed successfully"}, status=status.HTTP_201_CREATED)
#                     else:
#                         return Response({"detail": "Invalid order data"}, status=status.HTTP_400_BAD_REQUEST)

#                 except jwt.InvalidTokenError:
#                     return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
#                 except User.DoesNotExist:
#                     return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


                








