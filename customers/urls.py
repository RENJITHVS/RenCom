from django.urls import path

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.index, name='home'),
    path('login/',views.customerLogin, name="loginUser"),
    path('signup/',views.customerSignup, name="signupUser"),
    path("activate/<slug:uidb64>/<slug:token>)/", views.account_activate, name="activate"),
]