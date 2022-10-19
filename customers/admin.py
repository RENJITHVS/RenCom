from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_summernote.models import Attachment

from .models import Address, Customer, CustomerProfile, User, VendorUser
from vendors.models import VendorProfile

from django.contrib.auth.models import Group
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'last_login', 'date_joined', 'is_active', 'email_verified')
    list_display_links = ('email', 'full_name',)
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
admin.site.register(Customer, AccountAdmin)
admin.site.register(VendorUser, AccountAdmin)
admin.site.register(CustomerProfile)
admin.site.register(VendorProfile)
admin.site.register(Address)
admin.site.unregister(Group)
admin.site.unregister(Attachment)