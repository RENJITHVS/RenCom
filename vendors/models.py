from django.conf import settings
from django.db import models


# Create your models here.

class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vendor_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.full_name
