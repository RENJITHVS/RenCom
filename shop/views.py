
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .models import Category, Product, ProductAttribute
from .forms import ProductFilter, AddProductForm, ProductVarationFormset, AddProductImagesForm
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
# Create your views here.



def all_products(request):
    filtered_products = ProductFilter(
        request.GET, queryset=Product.products.all())

    productQs = filtered_products.qs
    paginated_by = 20
    paginator = Paginator(productQs, paginated_by)
    page = request.GET.get('page')
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)

    context = {
        'products': filtered_products,
        'page_obj': products_paginated,
        'no_search': True
    }
    return render(request, 'shops/all_products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "shops/product_page.html", {"product": product})


def add_products(request):
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user.vendorprofile
            product.save()
            messages.success(
                request, "Product details added ! Please add any varations")
            return HttpResponseRedirect(reverse('shop:add_product_variations', kwargs={'prodslug': product.slug}))
    if request.method == "GET":
        form = AddProductForm(request.GET or None)
    return render(request, 'shops/add_products.html', {'form': form, })


def add_products_varations(request, prodslug):
    product = get_object_or_404(Product, slug=prodslug)
    formset = ProductVarationFormset(queryset=ProductAttribute.objects.none())
    if request.method == "POST":
        formset = ProductVarationFormset(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            print(instances)
            for instance in instances:
                print(instance)
                instance.product = product
                instance.save()
            messages.success(request, "Product Varaition added Successfully")
        return HttpResponseRedirect(reverse('shop:add_products_images', kwargs={'prodslug': product.slug}))

    return render(request, 'shops/add_products_variations.html', {'formset': formset})


def add_products_images(request, prodslug):
    product = get_object_or_404(Product, slug=prodslug)
    if request.method == "POST":
        form = AddProductImagesForm(request.POST , request.FILES , instance=product)
        if form.is_valid():
            form.save(commit=False)
            form.is_active = True
            form.save()
            messages.success(request, "Product images added successfully")
            return HttpResponseRedirect(reverse('shop:product_preview', kwargs={'prodslug': product.slug}))
    form = AddProductImagesForm(instance=product)
    return render(request, 'shops/add_product_images.html', {'form': form})

def product_previews(request, prodslug):
    product = get_object_or_404(Product, slug=prodslug)
    return render(request,'shops/product_preview.html', {"product":product})

def category_list(request, prodslug):
    category = get_object_or_404(Category, slug = prodslug)
    products = Product.products.filter(category__in=category.get_descendants(True))
    paginated_by = 20
    paginator = Paginator(products, paginated_by)
    page = request.GET.get('page')
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)

    return render(request, 'shops/product_category_list', {"page_obj":products_paginated})