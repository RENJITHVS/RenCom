from django.conf import settings
import razorpay
import json
import datetime
from .paypal import PayPalClient
from paypalcheckoutsdk.orders import OrdersGetRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from customers.models import Address
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from cart.cart import Cart
from orders.models import Order, OrderItem, Coupon
from .forms import AddressFormSet
from shop.models import MARGIN

from notifications.signals import notify
from django.core.mail import EmailMultiAlternatives

# for generating pdf invoice
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa



# import os


def test_customer(user):
    if user.is_anonymous:
        return False
    return user.role == "CUSTOMER"


def test_vendor(user):
    if user.is_anonymous:
        return False
    return user.role == "VENDOR"


def generate_pdf(data):
    try:
        ## For generating Invoice PDF
        template = get_template("payment/payment_pdf_invoice.html")

        html = template.render(data)
        result = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("ISO-8859-1")), result
        )  # , link_callback=fetch_resources)
        pdf = result.getvalue()
        filename = "Invoice_" + data["order_id"] + ".pdf"

        mail_subject = "Rencom. Order details"

        context_dict = {
            "user": data["name"],
            "order_id": data["order_id"],
            "order": data["order"],
        }
        template = get_template("payment/payment_invoice.html")
        message = template.render(context_dict)
        to_email = data["order"].email

        # for including css(only inline css works) in mail and remove autoescape off
        email = EmailMultiAlternatives(
            mail_subject,
            "hello",  # necessary to pass some message here
            settings.EMAIL_HOST_USER,
            [to_email,],
        )
        email.attach_alternative(message, "text/html")
        email.attach(filename, pdf, "application/pdf")
        email.send(fail_silently=False)
        return True
    except:
        return False


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def add_billing_details(request):
    cart = Cart(request)
    user = request.user.customerprofile
    if request.method == "POST":
        formset = AddressFormSet(request.POST, instance=user)
        if formset.is_valid():
            formset.save()
            messages.success(request, "address added successfully")
            return redirect("payment:add-address")
    else:
        address_details = Address.objects.filter(customer=user)
        if address_details is not None:
            formset = AddressFormSet(instance=user)
        else:
            formset = AddressFormSet()
    return render(
        request, "payment/billing_info.html", {"formset": formset, "cart": cart}
    )


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def selectAddresses(request):
    session = request.session
    addresses = Address.objects.filter(customer=request.user.customerprofile).order_by(
        "-default"
    )
    if addresses.exists():
        if "address" not in request.session:
            session["address"] = {"address_id": str(addresses[0].id)}
        else:
            session["address"]["address_id"] = str(addresses[0].id)
    return render(request, "payment/select_address.html", {"addresses": addresses})


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def set_default_address(request):
    if request.method == "POST":
        addresses = Address.objects.filter(customer=request.user.customerprofile)
        address_id = request.POST.get("addressid")
        for address in addresses:
            if address.default == True:
                address.default = False
                address.save()

        ad = get_object_or_404(Address, id=address_id)
        ad.default = True
        ad.save()
        response = JsonResponse({"success": True})
        return response


# payment checkout sdk
@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def set_payment_method(request):
    if "address" not in request.session:
        messages.warning(request, "Please select address option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    cart = Cart(request)
    price = cart.get_total_price() * 100
    if price < 1:
        messages.warning(request, "Please add something to cart")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    transfers = [ {"account":item['product'].created_by.razorpay_id,
            "amount": item['total_price']*(100-MARGIN*100),
            "currency": "INR",
            "notes":{
                "branch":"branch name",
                "name": 'xxxxxx'
            },
            "linked_account_notes":[
                "branch"
            ],
            "on_hold":0,} for item in cart]
    
    razorpay_client = razorpay.Client(
        auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET)
    )

    razor_payment = razorpay_client.order.create(
        {"amount": int(price),
         "currency": "INR", 
        "transfers":transfers})

    return render(request, "payment/payment_method.html", {"raz_payment": razor_payment})
    

@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def paypal_payment_complete(request):
    PPClient = PayPalClient()
    body = json.loads(request.body)
    data = body["orderID"]
    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)
    user_id = request.user.customerprofile.id
    address_id = request.session["address"]["address_id"]
    address = get_object_or_404(Address, id=address_id)

    cart = Cart(request)
    order = Order.objects.create(
        user_id=user_id,
        full_name=address.full_name,
        email=request.user.email,
        city=address.city,
        address1=address.address_line,
        address2=address.address_line,
        pincode=address.pincode,
        phone=address.phone,
        total_paid=cart.get_total_price(),
        order_key=response.result.id,
        payment_option="paypal",
        billing_status=True,
    )

    order_id = order.pk

    for item in cart:
        order_item = OrderItem.objects.create(
            order_id=order_id,
            product=item["product"],
            price=item["price"],
            quantity=item["qty"],
        )
        notify.send(
                request.user,
                recipient=item["product"].created_by.user,
                verb=f"A order is placed with {order_item.order.order_key} and Payed Rs {order_item.price}",
            )

    data = {
        "order_id": str(order_id),
        "transaction": "PAYPAL",
        "user_email": request.user.email,
        "date": str(order.created),
        "name": address.full_name,
        "order": order,
        "amount": cart.get_total_price(),
    }

    # create PDF and mail to user
    pdf = generate_pdf(data)
    if pdf:
        messages.success(
            request, "Order placed successfully, invoice sent to your mail id"
        )
    else:
        messages.success(request, "Order placed successfully, invoice not generated")

    return JsonResponse("Payment completed!", safe=False)


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def razorpay_payment_complete(request):
    body = json.loads(request.body)
    razorpay_client = razorpay.Client(
        auth=(str(settings.RAZOR_PAY_KEY_ID), str(settings.KEY_SECRET))
    )
    razorpay_client.set_app_details({"title": "Rencom", "version": "1.1v"})
    cart = Cart(request)

    try:
        razorpay_client.utility.verify_payment_signature(body)
        address_id = request.session["address"]["address_id"]
        address = get_object_or_404(Address, id=address_id)
        user_id = request.user.customerprofile.id
        email = request.user.email

        order = Order.objects.create(
            user_id=user_id,
            full_name=address.full_name,
            email=email,
            city=address.city,
            address1=address.address_line,
            address2=address.address_line,
            pincode=address.pincode,
            phone=address.phone,
            total_paid=cart.get_total_price(),
            order_key=body["razorpay_order_id"],
            payment_id=body["razorpay_payment_id"],
            payment_option="razorpay",
            billing_status=True,
        )
        order_id = order.pk

        for item in cart:
            order_item = OrderItem.objects.create(
                order_id=order_id,
                product=item["product"],
                price=item["price"],
                quantity=item["qty"],
            )
            notify.send(
                request.user,
                recipient=item["product"].created_by.user,
                verb=f"A order is placed with {order_item.order.order_key} and Payed Rs {order_item.price}",
            )

        data = {
            "order_id": str(order.order_key),
            "transaction": "Razorpay",
            "user_email": email,
            "date": str(order.created),
            "name": address.full_name,
            "order": order,
            "amount": cart.get_total_price(),
        }

        # create PDF and mail to user
        pdf = generate_pdf(data)
        if pdf:
            messages.success(request, "Order placed successfully, invoice sent to your mail id")
        else:
            messages.success(request, "Order placed successfully, invoice not generated")

        return JsonResponse("Payment completed!", safe=False)
    except:
        raise Exception("internal errors")


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def order_without_payment(request):
    cart = Cart(request)
    address_id = request.session["address"]["address_id"]

    address = get_object_or_404(Address, id=address_id)
    user_id = request.user.customerprofile.id
    email = request.user.email

    order = Order.objects.create(
        user_id=user_id,
        full_name=address.full_name,
        email=email,
        city=address.city,
        address1=address.address_line,
        address2=address.address_line,
        pincode=address.pincode,
        phone=address.phone,
        total_paid=cart.get_total_price(),
        order_key=datetime.datetime.now().strftime("%m%d%M%S") + str(email),
        payment_option="Cash-on-delivery",
        billing_status=False,
    )
    order_id = order.pk
    for item in cart:
        OrderItem.objects.create(
            order_id=order_id,
            product=item["product"],
            price=item["price"],
            quantity=item["qty"],
        )
        product = item["product"]
        notify.send(
            sender=request.user,
            recipient=product.created_by.user,
            verb=f"Order placed by {request.user.customerprofile} as COD",
        )

    data = {
        "order_id": str(order.order_key),
        "transaction": "Cash On Delivery",
        "user_email": email,
        "date": str(order.created),
        "name": address.full_name,
        "order": order,
        "amount": cart.get_total_price(),
    }


    # create PDF and mail to user
    pdf = generate_pdf(data)
    if pdf:
        messages.success(
            request, "Order placed successfully, invoice sent to your mail id"
        )
    else:
        messages.success(request, "Order placed successfully, invoice not generated")
    return redirect("payment:payment_successful")


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def payment_successful(request):
    cart = Cart(request)
    cart.clear()
    if "coupon" in request.session:
        coupon = request.session["coupon"]
        coupon_data = get_object_or_404(Coupon, code=coupon)
        coupon_data.used_users.add(request.user.customerprofile)
        del request.session["coupon"]

    messages.success(request, " your orders placed Successfully")
    return redirect("orders:view-orders")
