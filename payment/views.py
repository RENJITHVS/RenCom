
from django.conf import settings
import razorpay
import json
from .paypal import PayPalClient
from paypalcheckoutsdk.orders import OrdersGetRequest
from django.contrib.auth.decorators import login_required
from customers.models import Address
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from cart.cart import Cart
from orders.models import Order, OrderItem


@login_required
def selectAddresses(request):
    session = request.session
    addresses = Address.objects.filter(
        customer=request.user.customerprofile).order_by("-default")
    if "address" not in request.session:
        session['address'] = {'address_id': str(addresses[0].id)}
    else:
        session['address']['address_id'] = str(addresses[0].id)
    return render(request, 'payment/select_address.html', {'addresses': addresses})


@login_required
def set_default_address(request):
    if request.method == 'POST':
        addresses = Address.objects.filter(
            customer=request.user.customerprofile)
        address_id = request.POST.get('addressid')
        for address in addresses:
            if address.default == True:
                address.default = False
                address.save()

        ad = get_object_or_404(Address, id=address_id)
        ad.default = True
        ad.save()
        response = JsonResponse({'success': True})
        return response


# payment checkout sdk


@login_required
def set_payment_method(request):
    if "address" not in request.session:
        messages.success(request, "Please select address option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    cart = Cart(request)
    price = cart.get_total_price() * 100
    razorpay_client = razorpay.Client(
        auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
    razor_payment = razorpay_client.order.create(
        {'amount': int(price), 'currency': 'INR', 'payment_capture': 1})
    return render(request, 'payment/payment_method.html', {'raz_payment': razor_payment})


@login_required
def paypal_payment_complete(request):
    PPClient = PayPalClient()

    body = json.loads(request.body)
    data = body["orderID"]
    user_id = request.user.customerprofile.id
    address_id = request.session['address']['address_id']
    address = get_object_or_404(Address, id=address_id)

    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)

    cart = Cart(request)
    order = Order.objects.create(
        user_id=user_id,
        full_name=address.full_name,
        email=request.user.email,
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
        OrderItem.objects.create(
            order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

    return JsonResponse("Payment completed!", safe=False)


@login_required
def razorpay_payment_complete(request):

    body = json.loads(request.body)
    # print(body)
    orderid = body["orderID"]
    # payment_id = body["paymentID"]
    # signature = body["signature"]
    razorpay_client = razorpay.Client(
        auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
    check = razorpay_client.utility.verify_payment_signature(body)

    if check:
        return JsonResponse("Payment Failure", safe=False)

    address_id = request.session['address']['address_id']
    address = get_object_or_404(Address, id=address_id)
    user_id = request.user.customerprofile.id

    cart = Cart(request)
    order = Order.objects.create(
        user_id=user_id,
        full_name=address.full_name,
        email=request.user.email,
        address1=address.address_line,
        address2=address.address_line,
        pincode=address.pincode,
        phone=address.phone,
        total_paid=cart.get_total_price(),
        order_key=orderid,
        payment_option="razorpay",
        billing_status=True,
    )
    order_id = order.pk

    for item in cart:
        OrderItem.objects.create(
            order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

    return JsonResponse("Payment completed!", safe=False)


@login_required
def payment_successful(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, " your orders placed Successfully")
    return redirect('orders:view-orders')
