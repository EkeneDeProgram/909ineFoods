from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="user-registration"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("user_verification/", VerifyCodeView.as_view(), name="user-verification"),
    path("user_profile/", UserView.as_view(), name="user-profile"),
    path("logout/", LogoutView.as_view(), name="logout-user"),
    path("update_email/", UpdateEmailView.as_view(), name="update-email"),
    path("update_phone/", UpdatePhoneNumberView.as_view(), name="update-phone"),
    path("update_name/", UpdateUserNameView.as_view(), name="update-name"),
    path("update_address/", UpdateUserAddressView.as_view(), name="update-address"),
]