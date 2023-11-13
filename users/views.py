# Import third party modules
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status

# Import python standard modules
import jwt, datetime

# Import project modules
from .serializers import UserSerializer
from .models import User
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
    
    
# Define view to verify user verification code and generate JWT
class VerifyCodeView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the user's input verification code from the request
        user_input_code = request.data.get('verification_code') 

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
            return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        


# Defin view to retrieve user information based on a JWT stored in the request's cookies
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        # Check if the token is not present
        if not token:
            # Raise an AuthenticationFailed exception with a message
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)
        except jwt.ExpiredSignatureError:
            # If the decoding fails due to an expired signature, raise an AuthenticationFailed exception
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


# Defind view to logout user by deleting the JWT cookie
class LogoutView(APIView):
    def post(self, request):
        # Create a new Response object
        response = Response()
        # Delete the 'jwt' cookie from the response. 
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
