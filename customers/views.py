from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib import messages
from .forms import AddressFormSet, RegistrationForm, UserLoginForm, AddressForm
from .models import User, Address
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from shop.models import Product
from cart.cart import Cart


# Create your views here.


def index(request):
    product = Product.products.all()
    context = {
        'products': product
    }
    return render(request, "landing_page/home.html", context)


def CustomerloginPage(request):

    if request.user.is_authenticated:
        return redirect('customers:home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.warning(request, 'User does not exist Please Register')
            return redirect('customers:signupUser')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('customers:home')
        else:
            messages.error(request, "Email and passwoed doesn't match")

    return render(request, 'user/Userlogin.html')


def customerSignup(request):
    if request.user.is_authenticated:
        return redirect('customers:home')
    registerForm = RegistrationForm()

    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.full_name = registerForm.cleaned_data['full_name']
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.role = User.Role.CUSTOMER
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
                request, "User verification mail sent Successfully")
            return render(request, 'user/user_email_verification.html', {'form': registerForm})
    return render(request, "user/userSignup.html", {'form': registerForm})


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
        messages.success(
            request, f"Hi {user.full_name}! verification Successfull")
        return redirect('customers:home')
    else:
        messages.error(request, "User Verification Succesfull")
        return render(request, 'user/activation_invalid.html')

@login_required
def billing_details(request):
    cart = Cart(request)
    user = request.user.customerprofile
    if request.method == "POST":
        formset = AddressFormSet(request.POST,  instance=user)
        if formset.is_valid():
            formset.save()
            messages.success(request,'address added successfully')
            return redirect('customers:billing_details')
    else:
        address_details = Address.objects.filter(customer = user)
        if address_details is not None:
            formset = AddressFormSet(instance = user)
        else:
            formset = AddressFormSet()
    return render(request, 'orders/billing_info.html',{'formset': formset, 'cart': cart})

@login_required
def user_wishlist(request):
    products = Product.objects.filter(wishlist_user=request.user.customerprofile)
    return render(request, "cart/user_wishlist.html", {"wishlist": products})

@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.wishlist_user.filter(id=request.user.customerprofile.id).exists():
        product.wishlist_user.remove(request.user.customerprofile)
        messages.success(request, product.title + " has been removed from your WishList")
    else:
        product.wishlist_user.add(request.user.customerprofile)
        messages.success(request, "Added " + product.title + " to your WishList")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


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

