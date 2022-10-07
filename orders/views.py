from urllib import response
from django.http import JsonResponse
from django.shortcuts import render
from cart.cart import Cart
from .models import Order, OrderItem
# Create your views here.

# def add(request):
#     cart = Cart(request)
#     if request.method == 'post':
#         order_key = request.POST.get('order_key')
#         user_id = request.user.userprofile.id
#         carttotal = cart.get_total_price()

#         #check if order exist
#         if Order.objects.filter(order_key=order_key).exists():
#             pass
#         else:
#             order = Order.objects.create(user_id=user_id, full_name='name', address1='add1',
#                                 address2='add2', total_paid=carttotal, order_key=order_key)
#             order_id = order.pk

#             for item in cart:
#                 OrderItem.objects.create(order_id=order_id, product=item['product'], price=item['price'], quantity=item['qty'])
#         response = JsonResponse({'success': True})
#         return response