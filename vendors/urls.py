from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "vendors"

urlpatterns = [
    path("", views.vendor_home, name="vendor_home"),
    path("signup/", views.vendor_signup, name="vendor_signup"),
    path("login/", views.vendor_login, name="vendor_login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/vendor/login/"),
        name="vendor-logout",
    ),
    path("vendor_settings/", views.vendor_document_update, name="vendor_settings"),
     path("vendor_search/", views.search_products_vendor, name="vendor_search"),
]
