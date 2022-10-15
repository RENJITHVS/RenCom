from django.contrib import admin
from .models import Order , OrderItem, Coupon

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Coupon)
