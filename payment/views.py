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
from orders.models import Order, OrderItem, Coupon
from .forms import AddressFormSet


@login_required
def add_billing_details(request):
    cart = Cart(request)
    user = request.user.customerprofile
    if request.method == "POST":
        formset = AddressFormSet(request.POST,  instance=user)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'address added successfully')
            return redirect('payment:add-address')
    else:
        address_details = Address.objects.filter(customer=user)
        if address_details is not None:
            formset = AddressFormSet(instance=user)
        else:
            formset = AddressFormSet()
    return render(request, 'payment/billing_info.html', {'formset': formset, 'cart': cart})


@login_required
def selectAddresses(request):
    session = request.session
    addresses = Address.objects.filter(
        customer=request.user.customerprofile).order_by("-default")
    if addresses.exists():
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
        messages.warning(request, "Please select address option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    cart = Cart(request)
    price = cart.get_total_price() * 100
    if price < 1:
        messages.warning(request, "Please add something to cart")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

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
    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)
    user_id = request.user.customerprofile.id
    address_id = request.session['address']['address_id']
    coupon = request.session['coupon']
    address = get_object_or_404(Address, id=address_id)

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

    if 'coupon' in request.session:
        coupon = request.session['coupon']
        coupon_data = get_object_or_404(Coupon, code=coupon)
        # order = get_object_or_404(Order,id = order_id)
        # order.coupon.add(coupon_data)
        del request.session['coupon']
        coupon_data.used_users.add(request.user.customerprofile)

    return JsonResponse("Payment completed!", safe=False)


@login_required
def razorpay_payment_complete(request):
    body = json.loads(request.body)
    razorpay_client = razorpay.Client(
        auth=(str(settings.RAZOR_PAY_KEY_ID), str(settings.KEY_SECRET)))
    cart = Cart(request)

    try:
        razorpay_client.utility.verify_payment_signature(body)

        address_id = request.session['address']['address_id']

        address = get_object_or_404(Address, id=address_id)
        user_id = request.user.customerprofile.id

        order = Order.objects.create(
            user_id=user_id,
            full_name=address.full_name,
            email=request.user.email,
            address1=address.address_line,
            address2=address.address_line,
            pincode=address.pincode,
            phone=address.phone,
            total_paid=cart.get_total_price(),
            order_key=body["razorpay_order_id"],
            payment_option="razorpay",
            billing_status=True,
        )
        order_id = order.pk

        for item in cart:
            OrderItem.objects.create(
                order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"],)

        if 'coupon' in request.session:
            coupon = request.session['coupon']
            coupon_data = get_object_or_404(Coupon, code=coupon)
            # order = get_object_or_404(Order,id = order_id)
            # order.coupon.add(coupon_data)
            del request.session['coupon']
            request.session.modified = True
            coupon_data.used_users.add(request.user.customerprofile)

        return JsonResponse("Payment completed!", safe=False)
    except:
        raise Exception("internal errors")


@login_required
def payment_successful(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, " your orders placed Successfully")
    return redirect('orders:view-orders')
