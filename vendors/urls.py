from django.urls import path
from .views import *

urlpatterns = [
    path("create_vendor/", CreateVendorView.as_view(), name="vendor-create"),
    path("verify_vendor/", VerifyCodeView.as_view(), name="verify-vendor"),
    path("login_vendor/", LoginVendorView.as_view(), name="login-vendor"),
    path("get_vendor/", VendorView.as_view(), name="get-vendor"),
    path("logout_vendor/", LogoutVendorView.as_view(), name="logout-vendor"),
    path("delete_vendor/", VendorDeleteAccountView.as_view(), name="delete-vendor"),
    # Update vendor profile urls
    path("update_vendor_email/", UpdateVendorEmailView.as_view(), name="update-vendor-email"),
    path("update_vendor_contact_info/", UpdateVendorContactInfoView.as_view(), name="update-vendor-contact_info"),
    path("update_vendor/", UpdateVendorNameAndDescriptionView.as_view(), name="update-vendor"),
    path("update_vendor_image/", UpdateVendorImageView.as_view(), name="update-vendor-image"),
    # location urls
    path("add_location/", AddVendorLocationView.as_view(), name="add-location"),
    path("delete_location/<int:location_id>/", DeleteVendorLocationView.as_view(), name="delete-location"),
    # menu urls
    path("add_item/", AddMenuItemView.as_view(), name="add-item"), 
    path("vendor_menu/", VendorMenuView.as_view(), name="vendor-menu"),  
    path("vendor_menu_by_category/<int:category_id>/", VendorItemsByCategoryView.as_view(), name="vendor-menu-by-category"),
    path("delete_item/<int:item_id>/", DeleteVendorItemView.as_view(), name="delete-item"), 
    path("update_item/<int:item_id>/", UpdateItemView.as_view(), name="update-item"), 
]