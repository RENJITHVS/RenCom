from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import UserLoginForm

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.index, name='home'),
    # path(
    #     "login/",
    #     auth_views.LoginView.as_view(template_name="user/userlogin.html", form_class=UserLoginForm),
    #     name="loginUser",
    # ),
    path('login/', views.CustomerloginPage, name='loginUser'),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logoutUser"),
    path('signup/',views.customerSignup, name="signupUser"),
    path("activate/<slug:uidb64>/<slug:token>)/", views.account_activate, name="activate"),
]