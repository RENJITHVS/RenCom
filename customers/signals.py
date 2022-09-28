from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Customer, CustomerProfile, VendorUser, VendorProfile


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if not created:
        if instance.email_verified and instance.role == "CUSTOMER":
            CustomerProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=VendorUser)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and instance.role == "VENDOR":
        VendorProfile.objects.create(user=instance)
