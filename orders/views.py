from urllib import response
from django.http import JsonResponse
from django.shortcuts import render
from cart.cart import Cart
from .models import Order, OrderItem
from shop.models import Product
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def user_orders(request):
    user_id = request.user.customerprofile.id
    cart_order = Order.objects.filter(
        user_id=user_id).filter(billing_status=True)
    print(cart_order)
    orders = OrderItem.objects.filter(order__in=cart_order)
    return render(request, 'orders/order_details.html', {'orders': orders})
