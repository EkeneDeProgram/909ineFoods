from django.db import models
from django.contrib.auth.models import AbstractUser 
from phonenumbers import parse
from .managers import UserManager


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)


class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    hashed_verification_code = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_login = models.BooleanField(default=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)
  
  

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Remove 'email' from REQUIRED_FIELDS

    # Add related_name arguments to resolve the clash
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_users",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_users",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    # Override the save method to normalize the phone number before saving it
    def save(self, *args, **kwargs):
        # Parse the phone number to extract its components
        parsed_number = parse(self.phone_number, None)
        # Reformat the phone number to include a plus sign and the country code, followed by the national number
        self.phone_number = f"+{parsed_number.country_code}{parsed_number.national_number}"
        # Call the save method of the parent class (AbstractUser) to save the custom user instance
        super().save(*args, **kwargs)




