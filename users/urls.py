from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="user_registration"),
    path("login/", LoginView.as_view(), name="user_login"),
    path("user_verification/", VerifyCodeView.as_view(), name="user_verification"),
    path("user_profile/", UserView.as_view(), name="user_profile"),
    path("logout/", LogoutView.as_view(), name="logout_user"),
    path("update_email/", UpdateEmailView.as_view(), name="update_email"),
    path("update_phone/", UpdatePhoneNumberView.as_view(), name="update_phone"),
    path("update_name/", UpdateUserNameView.as_view(), name="update_name"),
    path("update_address/", UpdateUserAddressView.as_view(), name="update_address"),
    path("resend_verification_code/", ResendVerificationCodeView.as_view(), name="resend_verification_code"),
    path("update_user_image/", UpdateUserImageView.as_view(), name="update_user_image"),
    path("delete_user/", UserDeleteAccountView.as_view(), name="delete_user"),
    # user & vendor urls
    path("list_vendors/", ListActiveVendorsView.as_view(), name="list_vendors"),
    path("vendor_details/<int:vendor_id>/", VendorDetailsView.as_view(), name="vendor_details"),
    path("vendor_menu/<int:vendor_id>/", VendorMenuView.as_view(), name="vendor_menu"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("vendors_by_category/<int:category_id>/", VendorsByCategoryView.as_view(), name="vendors_by_category"),
    # Search urls
    path("search_vendors/", SearchVendorsView.as_view(), name="search-vendors"),
    path("search_Dishes/", SearchDishesView.as_view(), name="search-Dishes"),
    path("search_category/", SearchDishesByCategoryView.as_view(), name="search-category"),
    path("search_price/", SearchDishesByPriceView.as_view(), name="search-price"),
    path("search_location/", SearchVendorByLocationView.as_view(), name="search-location"),


]