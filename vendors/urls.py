from django.urls import path
from .views import *

urlpatterns = [
    path("create_vendor/", CreateVendorView.as_view(), name="vendor-create"),
    path("verify_vendor/", VerifyCodeView.as_view(), name="verify-vendor"),
    path("login_vendor/", LoginVendorView.as_view(), name="login-vendor"),
    path("get_vendor/", VendorView.as_view(), name="get-vendor"),
    path("logout_vendor/", LogoutVendorView.as_view(), name="logout-vendor"),
    path("delete_vendor/", VendorDeleteAccountView.as_view(), name="delete-vendor"),
    # Update urls
    path("update_vendor_email/", UpdateVendorEmailView.as_view(), name="update-vendor-email"),
    path("update_vendor_contact_info/", UpdateVendorContactInfoView.as_view(), name="update-vendor-contact_info"),
    path("update_vendor/", UpdateVendorNameAndDescriptionView.as_view(), name="update-vendor"),
    # location urls
    path("add_location/", AddVendorLocationView.as_view(), name="add_location"),
    path("delete_location/<int:location_id>/", DeleteVendorLocationView.as_view(), name="delete_location"),
       
]