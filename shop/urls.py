from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path('', views.all_products, name='shop_home'),
    path('<slug:slug>', views.product_detail, name='product_details'),
    
]