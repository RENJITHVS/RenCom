from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from shop.models import Product
from django.contrib import messages

from .cart import Cart
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger


def cart_items(request):
    cart = Cart(request)
    return render(request, 'cart/cart_page.html', {'cart': cart})


def cart_add_product(request):
    cart = Cart(request)
    if request.method == 'POST':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(Product, id=product_id)
        print(product)
        cart.add(product=product, qty=product_qty)
        cartqty = cart.__len__()
        response = JsonResponse({'qty': cartqty})
        messages.success(request, 'product added successfully')
        return response


def cart_delete_product(request):
    cart = Cart(request)
    if request.method == 'POST':
        product_id = int(request.POST.get('productid'))
        cart.delete(product=product_id)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()
        print(cartqty)
        response = JsonResponse({'qty': cartqty, 'subtotal': carttotal})
        return response


def cart_update_product(request):
    cart = Cart(request)
    if request.method == 'POST':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, qty=product_qty)
        cartqty = cart.__len__()
        carttotal = cart.get_total_price()
        response = JsonResponse({'qty': cartqty, 'subtotal': carttotal})
        return response
