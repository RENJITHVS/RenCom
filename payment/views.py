
from django.contrib.auth.decorators import login_required
from customers.models import Address
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from cart.cart import Cart
from orders.models import Order, OrderItem



@login_required
def selectAddresses(request):
    session = request.session
    addresses = Address.objects.filter(customer = request.user.customerprofile).order_by("-default");
    if "address" not in request.session:
        session['address'] = {'address_id': str(addresses[0].id)}
    else:
        session['address']['address_id'] = str(addresses[0].id)
    return render( request, 'payment/select_address.html', {'addresses' : addresses})

@login_required
def set_default_address(request):
    if request.method == 'POST':
        addresses = Address.objects.filter(customer = request.user.customerprofile)
        address_id = request.POST.get('addressid')
        for address in addresses:
            if address.default== True:
                address.default=False
                address.save()

        product = get_object_or_404(Address, id=address_id)
        product.default = True
        product.save()
        response = JsonResponse({'success':True})
        return response


# payment checkout sdk
from paypalcheckoutsdk.orders import OrdersGetRequest
from .paypal import PayPalClient
import json
import razorpay
from django.conf import settings

@login_required
def set_payment_method(request):
    if "address" not in request.session:
        messages.success(request, "Please select address option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    
    cart = Cart(request)
    price = cart.get_total_price() * 100
    razorpay_client = razorpay.Client(auth  = (settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
    razor_payment = razorpay_client.order.create({'amount': int(price) , 'currency': 'INR', 'payment_capture' : 1 })
    print(razor_payment)
    return render(request, 'payment/payment_method.html',{'raz_payment': razor_payment })

@login_required
def paypal_payment_complete(request):
    PPClient = PayPalClient()

    body = json.loads(request.body)
    data = body["orderID"]
    user_id = request.user.customerprofile.id

    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)

    cart = Cart(request)
    order = Order.objects.create(
        user_id=user_id,
        full_name=response.result.purchase_units[0].shipping.name.full_name,
        email=response.result.payer.email_address,
        address1=response.result.purchase_units[0].shipping.address.address_line_1,
        address2=response.result.purchase_units[0].shipping.address.admin_area_2,
        pincode=response.result.purchase_units[0].shipping.address.postal_code,
        total_paid= response.result.purchase_units[0].amount.value,
        order_key=response.result.id,
        payment_option="paypal",
        billing_status=True,
    )
    order_id = order.pk

    for item in cart:
        OrderItem.objects.create(order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

    return JsonResponse("Payment completed!", safe=False)


@login_required
def payment_successful(request):
    cart = Cart(request)
    cart.clear()
    return render(request, "cart/cart_page.html", {})