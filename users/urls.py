from django.urls import path
from .views import RegistrationView, VerifyCodeView, UserView, LogoutView, LoginView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="user-registration"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("user_verification/", VerifyCodeView.as_view(), name="user-verification"),
    path("user_profile/", UserView.as_view(), name="user-profile"),
    path("logout/", LogoutView.as_view(), name="logout-user"),
    
]