from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect
from cart.cart import Cart
from .models import Order, OrderItem, Coupon
from shop.models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .froms import RefundForm
import json
from notifications.signals import notify
from django.contrib.auth.decorators import user_passes_test, login_required

# Create your views here.


def test_customer(user):
    if user.is_anonymous:
        return False
    return user.role == "CUSTOMER"


def test_vendor(user):
    if user.is_anonymous:
        return False
    return user.role == "VENDOR"


def test_admin(user):
    if user.is_anonymous:
        return False
    return user.role == "ADMIN"


def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST["coupon"]
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if request.user.customerprofile in coupon.used_users.all():
                messages.warning(request, "You already used this coupon")
            else:
                request.session["coupon"] = coupon.code
                messages.success(request, "Coupon Added Successfully")
            return redirect("cart:cart_items")
        except ObjectDoesNotExist:
            messages.info(request, "Sorry This coupon does not exist")
    return redirect("cart:cart_items")


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def user_orders(request):
    user_id = request.user.customerprofile.id
    cart_order = Order.objects.filter(user_id=user_id)
    orders = OrderItem.objects.filter(order__in=cart_order)
    return render(request, "orders/order_details.html", {"orders": orders})


@user_passes_test(test_customer, login_url="/login/", redirect_field_name="next")
def user_cancel_order_request(request, order_id, order_item_id):
    order_details = Order.objects.get(id=order_id, user=request.user.customerprofile)
    order_item = OrderItem.objects.get(id=order_item_id)
    if (
        not order_details.billing_status
        and not order_details.payment_option == "Cash On Delivery"
    ):
        messages.warning(request, "you are not yet paid! for this order")
        return redirect("orders:view-orders")
    if order_item.refund_requested:
        messages.warning(request, "you are already applied for refund")
        return redirect("orders:view-orders")
    if request.method == "POST":
        form = RefundForm(request.POST)
        if form.is_valid():
            try:
                data = form.save(commit=False)
                order = order_details
                data.order = order
                data.orderItem = order_item
                data.save()
                orderitem = order_item
                orderitem.refund_requested = True
                orderitem.order_status = "Cancelled"
                orderitem.save()

                # notify.send(request.user.customerprofile, recipient=, verb=f"Refund request arise for order {order.id}")
                messages.success(
                    request,
                    "your refund request was submitted! Notify Once refund is assigned",
                )
            except:
                messages.error(request, "sorry error occured")
            return redirect("orders:view-orders")
    else:
        form = RefundForm()
    return render(request, "orders/refund_request.html", {"form": form})


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def vendor_orders_list(request):
    products = Product.objects.filter(created_by=request.user.vendorprofile.id)
    orders = OrderItem.objects.filter(product__in=products)
    context = {"orders": orders}
    return render(request, "vendor-orders/order-list.html", context)


@user_passes_test(test_vendor, login_url="/vendor/login", redirect_field_name="next")
def vendor_order_update_status(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        order_status = request.POST.get("order_status")
        order = get_object_or_404(OrderItem, id=order_id)
        if order.order_status == "Cancelled":
            return JsonResponse({"status": False})
        if order.order_status == "Delivered":
            return JsonResponse({"status": False})

        order.order_status = order_status
        order.save()
        if order.order_status == "Cancelled":
            notify.send(
                sender=request.user,
                recipient=order.order.user.user,
                verb=f"Sorry your order was cancelled",
            )
        if order.order_status == "Delivered":
            notify.send(
                sender=request.user,
                recipient=order.order.user.user,
                verb=f"Your order is delivered",
            )
            order.order.billing_status = True
        if order.order_status == "Shipped":
            notify.send(
                sender=request.user,
                recipient=order.order.user.user,
                verb=f"Your order is shipped",
            )
        return JsonResponse({"status": True})
