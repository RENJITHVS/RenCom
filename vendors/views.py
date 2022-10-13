from itertools import product
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from customers.forms import RegistrationForm
from customers.models import User, Address
from shop.models import Product
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from customers.tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import user_passes_test, login_required
from shop.forms import ProductFilter

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

def test_vendor(user):
    return user.role == "VENDOR"

# Create your views here.
@login_required(login_url='/vendor/login')
@user_passes_test(test_vendor ,login_url='/vendor/login',redirect_field_name='next')
def vendor_home(request):
    filtered_products = ProductFilter(
        request.GET, queryset=Product.objects.filter(created_by=request.user.vendorprofile.id))
    productQs = filtered_products.qs
    paginated_by = 20
    paginator = Paginator(productQs, paginated_by)
    page = request.GET.get('page')
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)

    context = {
        'products': filtered_products,
        'page_obj': products_paginated,
        'no_search': True
    }
    return render(request, 'vendor/home.html', context)

def vendor_signup(request):
    if request.user.is_authenticated and request.user.role == 'VENDOR':
        return redirect('vendor')
    registerForm = RegistrationForm()

    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.full_name = registerForm.cleaned_data['full_name']
            user.email = registerForm.cleaned_data['email'].lower()
            user.set_password(registerForm.cleaned_data['password'])
            user.role = User.Role.VENDOR
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            message = render_to_string('user/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            messages.success(
                request, "Vendor verification mail sent Successfully")
            return render(request, 'vendor/vendor_email_verification.html', {'form': registerForm})
    return render(request, "vendor/vendor-signup.html", {'form': registerForm})


def vendor_login(request):

    if request.user.is_authenticated and request.user.role == "VENDOR":
        return redirect('vendors:vendor_home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email, role = "VENDOR")
        except:
            messages.warning(request, 'User does not exist Please Register')
            return redirect('vendors:vendor_signup')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('vendors:vendor_home')
        else:
            messages.error(request, "Email and passwoed doesn't match")

    return render(request, 'vendor/vendor-login.html')
