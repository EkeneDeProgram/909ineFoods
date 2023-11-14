# Import third party modules
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status

# Import python standard modules
import jwt, datetime

# Import project modules
from .serializers import UserSerializer, AddressSerializer
from .models import User, Address
from .utils import *


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
        # Get the user's input verification code from the request
        email = request.data.get("email") 

        # Check if the email exists in the database
        user = get_user_model().objects.filter(email=email).first()

        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        verification_code = generate_verification_code() # Generate verification code for user
        hash_verification_code = hash_VC(verification_code) # Hash verification code

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
            hashed_input_code = hash_VC(user_input_code)
            user = User.objects.get(hashed_verification_code=hashed_input_code)

            if user: 
                user.is_verified = True
                user.is_login = True
                user.save()

                payload = {
                    "id": user.id,
                    "iat": datetime.datetime.utcnow()
                }

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
        


# Define view to retrieve user information based on a JWT stored in the request's cookies
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        # Check if the token is not present
        if not token:
            # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            # If the decoding fails due to an expired signature, raise an AuthenticationFailed exception
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
            # Decode the token to get the user ID
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        
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
            # Decode the token to get the user ID
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        
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
            # Decode the token to get the user ID
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the user
        user = get_user_model().objects.filter(id=payload["id"]).first()

        # Check if the user is found
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the new email already exists in the database
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

        # Get the new email from user
        new_first_name = request.data.get("first_name")
        new_last_name = request.data.get("last_name")

        # Check if the token is not present
        if not token:
           # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed("Unauthenticated!")
        
        try:
            # Decode the token to get the user ID
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        
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
            # Decode the token to get the user ID
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        
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





