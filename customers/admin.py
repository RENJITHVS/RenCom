from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_summernote.models import Attachment

from .models import Address, Customer, CustomerProfile, User, VendorUser, VendorProfiles
from django.contrib.auth.models import Group
from django.utils.html import format_html
from vendors.forms import RazorpayForm

# Register your models here.


class AddressInline(admin.TabularInline):
    model = Address


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html(
            '<img src="{}" width="40" style="border-radius: 50px;" />'.format(
                object.profile_pic.url
            )
        )

    thumbnail.short_description = "Photo"
    inlines = [
        AddressInline,
    ]
    list_display = (
        "thumbnail",
        "customer_name",
        "joined_on",
    )
    list_display_links = (
        "thumbnail",
        "customer_name",
    )
    search_fields = ("customer_name",)


@admin.register(VendorProfiles)
class VendorProfilesAdmin(admin.ModelAdmin):
    
    form = RazorpayForm
    def thumbnail(self, object):
        return format_html(
            '<img src="{}" width="40" style="border-radius: 50px;" />'.format(
                object.profile_pic.url
            )
        )

    thumbnail.short_description = "Photo"

    list_display = (
        "thumbnail",
        "vendor_name",
        "city",
        "vendor_id",
        "approved",
        "joined_on",
    )
    list_display_links = ("thumbnail", "vendor_name", "joined_on")
    search_fields = ("city",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "full_name",
        "is_active",
        "email_verified",
        "date_joined",
    )
    list_display_links = (
        "email",
        "full_name",
    )
    search_fields = ("full_name", "email")


@admin.register(VendorUser)
class VendorUserAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "full_name",
        "is_active",
        "email_verified",
        "date_joined",
    )
    list_display_links = (
        "email",
        "full_name",
    )
    search_fields = ("full_name", "email")


# admin.site.register(Address)
admin.site.unregister(Group)
admin.site.unregister(Attachment)
