from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path('', views.all_products, name='shop_home'),
    path('<slug:slug>', views.product_detail, name='product_details'),
    path('add_products/', views.add_products, name='add_products'),
    path('add_product_varations/<slug:prodslug>/',
         views.add_products_varations, name='add_product_variations'),
    path('add_product_images/<slug:prodslug>/',
         views.add_products_images, name='add_products_images'),
    path('product_preview/<slug:prodslug>/',
         views.product_previews, name='product_preview'),
    path('product_category/<slug:prodslug>/',
         views.category_list, name='category_list'),

]
