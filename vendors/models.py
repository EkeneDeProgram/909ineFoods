from django.db import models
from phonenumbers import parse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



# Define location model
class Location(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    vendor = models.ForeignKey("Vendor", on_delete=models.CASCADE, related_name="vendor_locations", default=None)

    class Meta:
        unique_together = ["vendor", "street", "city", "state"]

    def clean(self):
        # Check if the location already exists for the specific vendor
        if self.vendor.locations.filter(street=self.street, city=self.city, state=self.state).exists():
            raise ValidationError({"street": _("This location already exists for this vendor.")})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    

# Define Vendor model
class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    locations = models.ManyToManyField(Location, related_name="vendor_locations", blank=True)
    contact_info = models.CharField(max_length=15, unique=True,  null=True, blank=True)
    email = models.EmailField(unique=True)
    hashed_verification_code = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_login = models.BooleanField(default=False)
    registration_date = models.DateTimeField(default=timezone.now) 
    image = models.ImageField(upload_to="vendor_images/", null=True, blank=True)


    def add_location(self, street, city, state):
        # Create a new location and associate it with the vendor
        location = Location(street=street, city=city, state=state, vendor=self)
        location.full_clean()  # This will trigger the validation in the save method
        location.save()
        self.locations.add(location)


    # Override the save method to normalize the phone number before saving it
    def save(self, *args, **kwargs):
        # Parse the phone number to extract its components
        parsed_contact = parse(self.contact_info, None)
        # Reformat the phone number to include a plus sign and the country code, followed by the national number
        self.phone_number = f"+{parsed_contact.country_code}{parsed_contact.national_number}"
        # Call the save method of the parent class (AbstractUser) to save the custom user instance

        # Add the registration date and time if not already set
        if not self.registration_date:
            self.registration_date = timezone.now()

        super().save(*args, **kwargs)



# Define Category model
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    

# Define MenuItem model
class MenuItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_item_images/", null=True, blank=True)
    
