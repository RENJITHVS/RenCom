from django.shortcuts import render

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from shop.models import Product, ProductAttribute
from django.contrib import messages

from .cart import Cart
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from shop.forms import ProductFilter


# Create your views here.


def cart_items(request):
    cart = Cart(request)
    print(cart.__dict__)
    return render(request, "cart/cart_page.html", {"cart": cart})


def cart_add_product(request):
    cart = Cart(request)
    if request.method == "POST":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        variation_id = int(request.POST.get("variationid"))
        if cart.__len__() >= 10:
            return JsonResponse({"qty": "full"})
        product = get_object_or_404(Product, id=product_id)
        variation = get_object_or_404(ProductAttribute, id=variation_id)
        cart.add(product=product, qty=product_qty, variation=variation)
        cartqty = cart.__len__()
        response = JsonResponse({"qty": cartqty})
        messages.success(request, "product added successfully")
        return response


def cart_delete_product(request):
    cart = Cart(request)
    if request.method == "POST":
        product_id = int(request.POST.get("productid"))
        cart.delete(product=product_id)
        cartqty = cart.__len__()
        print(cartqty)
        response = JsonResponse({"qty": cartqty})
        return response


def cart_update_product(request):
    cart = Cart(request)
    if request.method == "POST":
        product_id = int(request.POST.get("productid"))
        product_qty = int(request.POST.get("productqty"))
        variation_id = int(request.POST.get("variationid"))
        # if cart.__len__() >= 10:
        #     return JsonResponse({"qty": "full"})
        cart.update(product=product_id, qty=product_qty, variation = variation_id)
        cartqty = cart.__len__()
        response = JsonResponse({"qty": cartqty})
        return response
