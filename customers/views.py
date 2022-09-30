from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib import messages
from .forms import RegistrationForm, UserLoginForm
from .models import User
from django.utils.encoding import force_bytes, force_str
from shop.models import Product

# Create your views here.
def index(request):
    product = Product.products.all()
    context={
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
            messages.success(request, "User verification mail sent Successfully")
            return render(request, 'user/user_email_verification.html', {'form': registerForm})
    return render(request, "user/userSignup.html", {'form': registerForm})

def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_verified = True
        user.save()
        login(request, user)
        messages.success(request, f"Hi {user.full_name}! verification Succesfull")
        return redirect('customers:home')
    else:
        messages.error(request, "User Verification Succesfull")
        return render(request, 'user/activation_invalid.html')