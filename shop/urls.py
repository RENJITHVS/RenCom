from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.all_products, name="shop_home"),
    path("search/", views.search_products, name="search"),
    path("<slug:slug>", views.product_detail, name="product_details"),
    path("add_products/", views.add_products, name="add_products"),
    path(
        "update_products/<slug:prodslug>/", views.update_products, name="update_product"
    ),
    path(
        "add_product_varations/<slug:prodslug>/",
        views.add_products_varations,
        name="add_product_variations",
    ),
    path(
        "add_product_images/<slug:prodslug>/",
        views.add_products_images,
        name="add_products_images",
    ),
    path(
        "product_preview/<slug:prodslug>/",
        views.product_previews,
        name="product_preview",
    ),
    path(
        "product_category/<slug:prodslug>/", views.category_list, name="category_list"
    ),
    path("product_delete/<slug:prodslug>", views.delete_product, name="delete_product"),
    path(
        "publish_product/<slug:prodslug>", views.publish_product, name="publish_product"
    ),
    path("add-review/<slug:slug>", views.add_review, name="add-review"),
    path(
        "add_extra_images/<slug:prodslug>/",
        views.add_products_images_extra,
        name="add_extra_images",
    ),
]
