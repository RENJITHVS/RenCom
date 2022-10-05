from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .models import Product
from .forms import ProductFilter

# Create your views here.


def all_products(request):
    filtered_products = ProductFilter(
        request.GET, queryset=Product.products.all())
    context = {
        'products': filtered_products,
        'no_search': True
    }
    return render(request, 'shops/all_products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "shops/product_page.html", {"product": product})
