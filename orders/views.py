from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, reverse
from cart.cart import Cart
from .models import Order, OrderItem, Coupon
from shop.models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.


@login_required
def user_orders(request):
    user_id = request.user.customerprofile.id

    cart_order = Order.objects.filter(
        user_id=user_id).filter(billing_status=True)
    print(cart_order)
    orders = OrderItem.objects.filter(order__in=cart_order)
    return render(request, 'orders/order_details.html', {'orders': orders})


def vendor_orders_list(request):
    products = Product.objects.filter(created_by=request.user.vendorprofile.id)
    orders = OrderItem.objects.filter(product__in=products)
    return render(request, 'orders/vendor_order_list.html', {'order': orders})


def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST['coupon']
        try:
            coupon = Coupon.objects.get(code =coupon_code)
            if request.user.customerprofile in coupon.used_users.all():
                messages.warning(request, "You already used this coupon")
            else:
                request.session['coupon'] = coupon.code
                messages.success(request, "Coupon Added Successfully")
            return redirect("cart:cart_items")
        except ObjectDoesNotExist:
            messages.info(request, "Sorry This coupon does not exist")
    return redirect("cart:cart_items")