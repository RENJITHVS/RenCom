from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("view_orders/", views.user_orders, name="view-orders"),
    path("apply-coupon/", views.apply_coupon, name="apply-coupon"),
    path("order_details/", views.vendor_orders_list, name="vendor-orders-list"),
    path(
        "order-details/",
        views.vendor_order_update_status,
        name="vendor_order_status_update",
    ),
    path(
        "user-cancel-order-request/<int:order_id>/<int:order_item_id>",
        views.user_cancel_order_request,
        name="user_cancel_order_request",
    ),
]
