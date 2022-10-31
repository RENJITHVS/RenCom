from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib import messages
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import User, Address
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from notifications.signals import notify
from shop.models import Product
from cart.cart import Cart
from cart.models import Basket, BasketItem
from shop.models import Banner

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

# Create your views here.
def test_customer(user):
    if user.is_anonymous:
        return False
    return user.role == "CUSTOMER"


def index(request):
    product = Product.products.all()
    paginated_by = 20
    paginator = Paginator(product, paginated_by)
    # add details form banner
    mob_banners = Banner.objects.filter(active=True, is_mobile = True).order_by("-id")[:3]
    desk_banners = Banner.objects.filter(active=True, is_mobile = False).order_by("-id")[:3]
    page = request.GET.get("page")
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)
    context = {
        "page_obj": products_paginated,
        "mob_banners": mob_banners,
        "desk_banners": desk_banners,
    }
    return render(request, "landing_page/home.html", context)


def CustomerloginPage(request):

    if request.user.is_authenticated:
        return redirect("customers:home")
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email, role="CUSTOMER")
        except:
            messages.warning(request, "User does not exist Please Register")
            return redirect("customers:signupUser")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            user = request.user.customerprofile
            cart = Cart(request)
            cart.load_from_db(user)
            try:
                return HttpResponseRedirect(request.GET["next"])
            except:
                return HttpResponseRedirect("/")
        else:
            messages.error(request, "Email and passwoed doesn't match")
    return render(request, "user/Userlogin.html")


def customerSignup(request):
    if request.user.is_authenticated and request.user.role == "CUSTOMER":
        return redirect("customers:home")
    registerForm = RegistrationForm()

    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.full_name = registerForm.cleaned_data["full_name"]
            user.email = registerForm.cleaned_data["email"]
            user.set_password(registerForm.cleaned_data["password"])
            user.role = User.Role.CUSTOMER
            user.save()
            current_site = get_current_site(request)
            subject = "Activate your Account"
            message = render_to_string(
                "user/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            messages.success(request, "User verification mail sent Successfully")
            return render(
                request, "user/user_email_verification.html", {"form": registerForm}
            )
        else:
            pass
    return render(request, "user/userSignup.html", {"form": registerForm})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_verified = True
        user.save()
        login(request, user)
        messages.success(request, f"Hi {user.full_name}! verification Successfull")
        if request.user.role == "VENDOR":
            notify.send(
                user,
                recipient=User.objects.filter(role="ADMIN"),
                verb="New Vendor added",
            )
            return redirect("vendors:vendor_settings")
        if request.user.role == "CUSTOMER":
            return redirect("customers:home")
        else:
            return render(request, "user/activation_invalid.html")

    else:
        messages.error(request, "User Verification Failed")
        return render(request, "user/activation_invalid.html")


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def user_wishlist(request):
    products = Product.objects.filter(wishlist_user=request.user.customerprofile)
    paginated_by = 5
    paginator = Paginator(products, paginated_by)
    page = request.GET.get("page")
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)

    return render(request, "cart/user_wishlist.html", {"page_obj": products_paginated})


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.wishlist_user.filter(id=request.user.customerprofile.id).exists():
        product.wishlist_user.remove(request.user.customerprofile)
        messages.warning(
            request, product.title + " has been removed from your WishList"
        )
    else:
        product.wishlist_user.add(request.user.customerprofile)
        messages.success(request, "Added " + product.title + " to your WishList")
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


# def add_billing_address(request):
#     user = request.user.customerprofile
#     try:
#         address = Address.objects.get(customer = user)
#         print("hi")
#         form = AddressForm(request.POST or None, instance=address)
#     except:
#         form = AddressForm(request.POST or None)
#     if request.method == "POST":
#         if form.is_valid():
#             print(form)
#             form.save()
#             messages.success(request, "address added successfully")
#             return redirect('customers:add_billing_address')
#         else:
#             messages.error(request, 'error occured')
#             return redirect('customers:add_billing_address')
#     return render(request, 'orders/billing_form.html', {'form': form})


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def view_settings(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.customerprofile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account detailshas been updated!")
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.customerprofile)
    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "user/settings.html", context)


@login_required
def logout_user(request):
    user = request.user

    if user.role == "VENDOR":
        logout(request)
        return redirect("vendors:vendor_login")
    elif user.role == "CUSTOMER":
        userprofile = user.customerprofile
        cart = Cart(request)
        cart.add_to_db(userprofile)
        logout(request)
        return redirect("customers:loginUser")
    else:
        logout(request)
        return redirect("customers:loginUser")


# {'price': 24000.0, 'qty': 2, 'delivery_price': 0.0, 'orginal_amount': 25999.0, 'color': 'Black', 'color_code': '#000000', 'product': <Product: Redmi K50i 5G (Stealth Black, 6GB RAM, 128GB Storage) | Flagship Mediatek Dimensity 8100 Processor | 144Hz Liquid FFS Display | Alexa Built-in>, 'total_price': 48000.0}
# {'price': 7000.0, 'qty': 2, 'delivery_price': 0.0, 'orginal_amount': 9000.0, 'color': 'White', 'color_code': '#FFFFFF', 'product': <Product: Casa Copenhagen Magic Collection, 70 L Personal Air Cooler with Anti Bacterial Honeycomb Pads, 3rd Turbo Fan, Powerful Air Throw, Auto Swing and 3-Speed Control, Low Power Consumption - Black/White>, 'total_price': 14000.0}
