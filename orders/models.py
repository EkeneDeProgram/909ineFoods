from django.db import models
from vendors.models import *
from users.models import *
from django.utils import timezone



# Define status model
class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)



# Define OrderItem model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_date = models.DateTimeField(default=timezone.now)
    delivered = models.BooleanField(default=False)
    paid_for = models.BooleanField(default=False)



# Define CartItem model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    








