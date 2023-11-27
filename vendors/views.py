# Import third party modules
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

# Import project modules
from .models import Vendor, Location, Menu
from .serializers import VendorSerializer, MenuSerializer
from users.utils import *

# Import python standard modules
import jwt, datetime


# Define view for vendor Creation
class CreateVendorView(CreateAPIView):
    serializer_class = VendorSerializer

    def perform_create(self, serializer):
        # Generate verification code for user
        verification_code = generate_verification_code()
        hash_verification_code = hash_VC(verification_code)

        # Save the vendor instance
        vendor = serializer.save(hashed_verification_code=hash_verification_code)

        # Send email verification code
        email = vendor.email
        send_verification_email(email, verification_code)

        # Serialize the vendor details to include id
        serialized_data = VendorSerializer(vendor).data

        # Return a custom response with vendor details and id
        return Response(serialized_data, status=status.HTTP_201_CREATED)
    

# Define view to login vendor
class LoginVendorView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the vendor's input email from the request
        email = request.data.get("email") 
        
        try:
            # Check if a vendor with the given email exists
            vendor = Vendor.objects.get(email=email)

            verification_code = generate_verification_code() # Generate verification code for user
            hash_verification_code = hash_VC(verification_code) # Hash verification code

            # Update and save vendor details
            vendor.hashed_verification_code = hash_verification_code 
            vendor.save()

            # Send email verification code 
            email = vendor.email
            send_verification_email(email, verification_code)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        except Vendor.DoesNotExist:
            return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)


# Define view to verify vendor 
class VerifyCodeView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the vendor's input verification code from the request
        vendor_input_code = request.data.get("verification_code") 

        try:
            hashed_input_code = hash_VC(vendor_input_code) # Hash user inputed verification code
            vendor = Vendor.objects.get(hashed_verification_code=hashed_input_code) # Get user with that email

            # If vendor Exists
            if vendor: 
                vendor.is_verified = True
                vendor.is_login = True
                vendor.save()

                # Create a payload dictionary containing information to be encoded in the JWT
                payload = {
                    "id": vendor.id,
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
        except Vendor.DoesNotExist:
            return Response({"detail": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)


# # Define view to retrieve Vendor information(Profile) based on a JWT stored in the request's cookies
class VendorView(APIView):
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
        
        vendor = Vendor.objects.filter(id=payload["id"]).first()
        serializer = VendorSerializer(vendor)
        response_data = {
            "Vendor": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK) 



# Define view to logout vendor   
class LogoutVendorView(APIView):
    def post(self, request, *args, **kwargs):
        # Clear the JWT token from the cookie to log the user out
        response = Response()
        response.delete_cookie("jwt")

        # Retrieve the current vendor, by decoding the JWT token
        jwt_token = request.COOKIES.get("jwt")
        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                # Update is_login to False
                vendor.is_login = False
                vendor.save()
                logout(request)
                response.data = {
                    "message": "Logout successful"
                }
            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to enable vendor delete thier account
class VendorDeleteAccountView(APIView):
    def delete(self, request, *args, **kwargs):
        response = Response()

        jwt_token = request.COOKIES.get("jwt")
        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                # Delete the vendor
                vendor.delete()
                response.data = {
                    "message": "Your account has been deleted successfully"
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to update vendor email
class UpdateVendorEmailView(APIView):
    def put(self, request, *args, **kwargs):

        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        # Get the new email from user
        new_email = request.data.get("email")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                verification_code = generate_verification_code() # Generate verification code for user
                hash_verification_code = hash_VC(verification_code) # Hash verification code

                # Update vendor details
                vendor.email = new_email
                vendor.hashed_verification_code = hash_verification_code
                vendor.is_verified = False
                vendor.save()
                
                # Send email verification code 
                send_verification_email(new_email, verification_code)
                response.data = {"message": "Email updated successfully"}

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to update vendor contact_info
class UpdateVendorContactInfoView(APIView):
    def put(self, request, *args, **kwargs):

        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        # Get the new contact info
        new_contact_info = request.data.get("contact_info")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                # Check if the new_contact_info already exists for another vendor
                if Vendor.objects.exclude(id=vendor_id).filter(contact_info=new_contact_info).exists():
                    return Response({"detail": "This contact_info already exists for another vendor."}, status=status.HTTP_400_BAD_REQUEST)

                # Update the contact_info
                vendor.contact_info = new_contact_info
                vendor.save()

                response.data = {
                    "message": "Contact info updated successfully."
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response


# Define view to update vendor name and description
class UpdateVendorNameAndDescriptionView(APIView):
    def put(self, request, *args, **kwargs):

        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        
        # Get the new name and description from vendor
        new_name = request.data.get("name")
        new_description = request.data.get("description")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                # Update vendor details
                if new_name:
                    vendor.name = new_name
                if new_description:
                        vendor.description = new_description
                vendor.save()

                response.data = {
                    "message": "update successfull"
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response


# Define view to add location to vendor
class AddVendorLocationView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        vendor_street = request.data.get("street")
        vendor_city = request.data.get("city")
        vendor_state = request.data.get("state")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                vendor = Vendor.objects.get(id=vendor_id)

                # Create a new location and associate it with the vendor
                location = Location(street=vendor_street, city=vendor_city, state=vendor_state, vendor=vendor)

                try:
                    location.save()
                    vendor.locations.add(location)
                    vendor.is_active = True
                    vendor.save()

                    response.data = {
                        "message": "Location created and associated with the vendor."
                    }
                except ValidationError as e:
                    return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to delete a particular location from vendor
class DeleteVendorLocationView(APIView):
    def delete(self, request, location_id, *args, **kwargs):
        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                vendor = Vendor.objects.get(id=vendor_id)

                # Check if the location exists and belongs to the vendor
                try:
                    location = Location.objects.get(id=location_id, vendor=vendor)
                except Location.DoesNotExist:
                    return Response({"detail": "Location not found or does not belong to the vendor"}, status=status.HTTP_404_NOT_FOUND)

                # Delete the location
                location.delete()

                response.data = {
                    "message": "Location deleted successfully."
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to add item to menu
class AddMenuItemView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        # Get data for the new menu item from the request
        category_id=request.data.get("category_id")
        name = request.data.get("name")
        description = request.data.get("description")
        price = request.data.get("price")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")

                # Create a new menu item
                menu_item = Menu.objects.create(
                    vendor_id=vendor_id,
                    category_id=category_id,  
                    name=name,
                    description=description,
                    price=price
                )

                # Serialize the new menu item and return the data
                serializer = MenuSerializer(menu_item)
                response.data = serializer.data
                response.status_code = status.HTTP_201_CREATED

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to Retrieve all vendor items(vendor menu)
class VendorMenuView(APIView):
    def get(self, request, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                vendor = Vendor.objects.get(id=vendor_id)

                # Retrieve all items added by the vendor
                items = Menu.objects.filter(vendor=vendor)

    
                # Serialize the items and return the data
                serializer = MenuSerializer(items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)


# Define view to get vendor menu by categories
class VendorItemsByCategoryView(APIView):
    def get(self, request, category_id, *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                vendor = Vendor.objects.get(id=vendor_id)

                # Retrieve all items added by the vendor for the specified category
                items = Menu.objects.filter(vendor=vendor, category=category_id)

    
                # Serialize the items and return the data
                serializer = MenuSerializer(items, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
            


# Define view to delete a particular item from menu
class DeleteVendorItemView(APIView):
    def delete(self, request, item_id, *args, **kwargs):
        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                vendor = Vendor.objects.get(id=vendor_id)

                # Check if the item exists and belongs to the vendor
                try:
                    item = Menu.objects.get(id=item_id, vendor=vendor)
                except Menu.DoesNotExist:
                    return Response({"detail": "Item not found or does not belong to the vendor"}, status=status.HTTP_404_NOT_FOUND)

                # Delete the location
                item.delete()

                response.data = {
                    "message": "Item deleted successfully."
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to update vendor item
class UpdateItemView(APIView):
    def put(self, request,  item_id, *args, **kwargs):

        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        
        # Get the new item name, description and price from vendor
        new_name = request.data.get("name")
        new_description = request.data.get("description")
        new_price = request.data.get("price")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                # Check if the item exists and belongs to the vendor
                try:
                    item = Menu.objects.get(id=item_id, vendor=vendor)
                except Menu.DoesNotExist:
                    return Response({"detail": "Item not found or does not belong to the vendor"}, status=status.HTTP_404_NOT_FOUND)


                # Update item details
                if new_name:
                    item.name = new_name
                if new_description:
                        item.description = new_description
                if new_price:
                    item.price = new_price
                item.save()

                response.data = {
                    "message": "update successfull"
                }

            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response
    

# Define view to update vendor profile image
class UpdateVendorImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def patch(self, request, *args, **kwargs):
        response = Response()
        jwt_token = request.COOKIES.get("jwt")

        # Get the image from the request
        image = request.data.get("image")

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")


                if not image:
                    return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
                
                vendor = Vendor.objects.get(id=vendor_id)
                
                # Update the vendor's image
                vendor.image = image
                vendor.save()
                response.data = {
                    "message": "update successfull"
                }
                    
            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return response
            

# Define view to update item  image
class UpdateItemImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request, item_id,  *args, **kwargs):
        jwt_token = request.COOKIES.get("jwt")

        # Retrieve the menu item instance or return a 404 response if not found
        menu_item = get_object_or_404(Menu, id=item_id)

        if jwt_token:
            try:
                decoded_payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITH])
                vendor_id = decoded_payload.get("id")
                # Retrieve the vendor from the database
                vendor = Vendor.objects.get(id=vendor_id)

                if vendor != menu_item.vendor:
                    return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

                # Assuming the user is the owner, update the image
                menu_item.image = request.data.get('image', menu_item.image)
                
                try:
                    # Save the updated menu item
                    menu_item.save()

                    # Serialize the updated menu item and return the data
                    serializer = MenuSerializer(menu_item)
                    return Response(serializer.data, status=status.HTTP_200_OK)

                except Exception as e:
                    # Handle validation errors or other exceptions
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            except jwt.InvalidTokenError:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            except Vendor.DoesNotExist:
                return Response({"detail": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

            



    
            


       