from django.conf import settings
from django.db import models
import datetime
from uuid import uuid4
from PIL import Image
from io import BytesIO
from django.core.files import File

# Create your models here.
def create_id():
    now = datetime.datetime.now()
    return str(now.year) + str(now.month) + str(now.day) + str(uuid4())[:7]


class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vendor_id = models.CharField(default=create_id, editable=False, max_length=30)
    profile_pic = models.ImageField(
        upload_to="profile_pic/",
        default="profile_pic.jpg",
    )
    address1 = models.CharField(max_length=250, blank=True, null=True)
    address2 = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=20, blank=True, null=True)
    document = models.FileField(upload_to="doc/", blank=True, null=True)
    approved = models.BooleanField(default=False)
    razorpay_id = models.CharField(max_length = 25, blank= True, null= True)
    

    def __str__(self):
        return self.user.full_name

    def vendor_name(self):
        return self.user.full_name

    vendor_name.short_description = "Name"

    def joined_on(self):
        return self.user.date_joined

    joined_on.short_description = "Joined on"

    def save(self, *args, **kwargs):
        img = Image.open(self.profile_pic)
        img.convert("RGB")
        img.save("name.jpg")
        img.thumbnail((300 , 300))

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        self.profile_pic = File(thumb_io, name=self.profile_pic.name)
        super(VendorProfile, self).save(*args, **kwargs)
