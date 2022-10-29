from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import UserLoginForm
from django.views.generic import TemplateView
from .forms import PwdResetForm, PwdResetConfirmForm

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.index, name="home"),
    # path(
    #     "login/",
    #     auth_views.LoginView.as_view(template_name="user/userlogin.html", form_class=UserLoginForm),
    #     name="loginUser",
    # ),
    path("login/", views.CustomerloginPage, name="loginUser"),
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.customerSignup, name="signupUser"),
    path(
        "activate/<slug:uidb64>/<slug:token>)/", views.account_activate, name="activate"
    ),
    path("wishlist/", views.user_wishlist, name="wishlist"),
    path("addwishlist/<int:id>/", views.add_to_wishlist, name="add_wishlist"),
    # Reset password
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="user/password_reset/password_reset_form.html",
            success_url="password_reset_email_confirm",
            email_template_name="user/password_reset/password_reset_email.html",
            form_class=PwdResetForm,
        ),
        name="pwdreset",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="user/password_reset/password_reset_confirm.html",
            success_url="password_reset_complete/",
            form_class=PwdResetConfirmForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset/password_reset_email_confirm/",
        TemplateView.as_view(template_name="user/password_reset/reset_status.html"),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/MTA/password_reset_complete/",
        TemplateView.as_view(template_name="user/password_reset/reset_status.html"),
        name="password_reset_complete",
    ),
    path("settings/", views.view_settings, name="settings-user"),
    # path('htmx/add-billing/', views.add_billing_address, name='add_billing_address'),
]
