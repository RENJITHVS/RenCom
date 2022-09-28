from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager
from vendors.models import VendorProfile

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"
        VENDOR = "VENDOR", "Vendor"
        OTHER = "OTHER", "Other"

    base_role = Role.OTHER

    role = models.CharField(max_length=50, choices=Role.choices)

    username = None
    email = models.EmailField(verbose_name='email address', unique=True)
    phone_number = PhoneNumberField(blank=True)
    full_name = models.CharField(max_length=220)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()
     
    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            'renjith@gmail.com',
            [self.email],
            fail_silently=False,
        )

    def save(self, *args, **kwargs):
        if not self.role:
            self.role = self.base_role
            # if self.email_verified or self.phone_verified:
            #     self.is_active = True;
            # else:
            #     self.is_active = False;
        return super().save(*args, **kwargs)


class CustomerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.CUSTOMER,email_verified= True)


class Customer(User):

    base_role = User.Role.CUSTOMER

    customer = CustomerManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Customers"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.full_name

class VendorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.VENDOR,email_verified= True)

class VendorUser(User):

    base_role = User.Role.VENDOR

    vendor = VendorManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Vendors"



