from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path('view_orders/', views.user_orders, name='view-orders'),
    path('vendor_order_details/', views.vendor_orders_list, name="vendor-orders"),
    path('apply-coupon/', views.apply_coupon, name="apply-coupon"),

]
