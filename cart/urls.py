from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_items, name="cart_items"),
    path("add/", views.cart_add_product, name="cart_add"),
    path("delete/", views.cart_delete_product, name="cart_delete"),
    path("update/", views.cart_update_product, name="cart_update"),
]
