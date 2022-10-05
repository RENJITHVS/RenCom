from django.contrib import admin

from .models import Address, Customer, CustomerProfile, User, VendorUser
# Register your models here.

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(VendorUser)
admin.site.register(CustomerProfile)
admin.site.register(Address)