from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q
from .models import Category, Product, ProductAttribute, ProductImage, ProductReview
from .forms import (
    ProductFilter,
    AddProductForm,
    ProductVarationFormset,
    AddProductImagesForm,
    ProductImageFormset,
)
from django.http import HttpResponseRedirect, JsonResponse

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from django.db.models import Avg, Count
import json

# Create your views here.


def test_vendor(user):
    if user.is_anonymous:
        return False
    return user.role == "VENDOR"


def test_customer(user):
    if user.is_anonymous:
        return False
    return user.role == "CUSTOMER"

def search_products(request):
        data_from_post = request.GET.get('title')
        payload = []
        if data_from_post:
            product_datas = Product.products.filter(title__icontains=data_from_post).values_list("title", flat=True)

            for product_data in product_datas:
                payload.append(product_data)
        
        return JsonResponse({'status': 200, 'data': payload}, safe=False)


def all_products(request):
    filtered_products = ProductFilter(request.GET, queryset=Product.products.all())
    productQs = filtered_products.qs
    paginated_by = 20
    paginator = Paginator(productQs, paginated_by)
    page = request.GET.get("page")
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)

    context = {
        "products": filtered_products,
        "page_obj": products_paginated,
        "no_search": True,
    }
    return render(request, "shops/all_products.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "shops/product_page.html", {"product": product})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def add_products(request):
    if not request.user.vendorprofile.approved:
        messages.warning(
            request, "sorry your profile is not yet verified!, Please try again later'"
        )
        return HttpResponseRedirect(reverse("vendors:vendor_home"))
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user.vendorprofile
            product.save()
            messages.success(
                request, "Product details added ! Please add any varations"
            )
            return HttpResponseRedirect(
                reverse(
                    "shop:add_product_variations", kwargs={"prodslug": product.slug}
                )
            )
    if request.method == "GET":
        form = AddProductForm(request.GET or None)
    return render(
        request,
        "shops/add_products.html",
        {
            "form": form,
        },
    )


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def update_products(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    if request.method == "POST":
        form = AddProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user.vendorprofile
            product.save()
            messages.success(
                request, "Product details updated  ! Please add any varations"
            )
            return HttpResponseRedirect(
                reverse(
                    "shop:add_product_variations", kwargs={"prodslug": product.slug}
                )
            )
    if request.method == "GET":
        form = AddProductForm(instance=product)
    return render(
        request,
        "shops/add_products.html",
        {
            "form": form,
        },
    )


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def add_products_varations(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    formset = ProductVarationFormset(queryset=ProductAttribute.product_attributes.filter(product=product.id),
    form_kwargs={'mrp': product.mrp_price})

    if request.method == "POST":
        formset = ProductVarationFormset(request.POST, form_kwargs={'mrp': product.mrp_price},)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.product = product
                instance.save()
            messages.success(request, "Product Varaition added Successfully")
            return HttpResponseRedirect(
            reverse("shop:add_products_images", kwargs={"prodslug": product.slug}))

    return render(request, "shops/add_products_variations.html", {"formset": formset, "mrp_price": product.mrp_price})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def add_products_images(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    if request.method == "POST":
        form = AddProductImagesForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save(commit=False)
            form.is_active = True
            form.save()
            messages.success(request, "Product images added successfully")
            return HttpResponseRedirect(
                reverse("shop:product_preview", kwargs={"prodslug": product.slug})
            )
    form = AddProductImagesForm(instance=product)
    return render(request, "shops/add_product_images.html", {"form": form})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def add_products_images_extra(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    formset = ProductImageFormset(
        queryset=ProductImage.objects.filter(product=product.id)
    )
    if request.method == "POST":
        formset = ProductImageFormset(
            request.POST,
            request.FILES,
        )
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.product = product
                instance.save()
            messages.success(request, "Product extra Images added successfully")
            return HttpResponseRedirect(
                reverse("shop:product_preview", kwargs={"prodslug": product.slug})
            )

    return render(request, "shops/add_extra_images.html", {"formset": formset})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def product_previews(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    return render(request, "shops/product_preview.html", {"product": product})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def publish_product(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    if request.method == "POST":
        if product.is_active:
            product.is_active = False
        else:
            product.is_active = True
        product.save()
        messages.success(request, "Your product Status Updated !")
        return redirect("vendors:vendor_home")
    else:
        messages.warning(request, "error occured")
        return render(request, "shops/product_preview.html", {"product": product})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def delete_product(request, prodslug):
    product = get_object_or_404(
        Product, slug=prodslug, created_by=request.user.vendorprofile
    )
    product.delete()
    messages.success(request, "product deleted successfully")
    return redirect("vendors:vendor_home")


def category_list(request, prodslug):
    category = get_object_or_404(Category, slug=prodslug)
    products = Product.products.filter(brand__in=category.get_descendants(True))
    paginated_by = 20
    paginator = Paginator(products, paginated_by)
    page = request.GET.get("page")
    try:
        products_paginated = paginator.get_page(page)
    except PageNotAnInteger:
        products_paginated = paginator.get_page(1)
    except EmptyPage:
        products_paginated = paginator.get_page(paginator.num_pages)

    return render(
        request, "shops/product_category_list.html", {"page_obj": products_paginated}
    )


@user_passes_test(test_customer, login_url="/login", redirect_field_name="next")
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    user = request.user.customerprofile
    try:
        ProductReview.objects.get(product=product, user=user)
        messages.warning(request, " you are already added review")
    except:
        ProductReview.objects.create(
            user=user,
            product=product,
            review_text=request.POST["review_text"],
            review_rating=request.POST["review_rating"],
        )
        messages.success(request, "review added")
    return redirect("shop:product_details", slug=slug)
