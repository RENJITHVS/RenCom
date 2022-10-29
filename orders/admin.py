from django.contrib import admin
from .models import Order, OrderItem, Coupon, Refund
from payment.razorpay import initate_refund_razorpay
from notifications.signals import notify


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("order", "product", "price", "quantity")
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "email",
        "city",
        "payment_option",
        "billing_status",
        "order_key",
    ]
    list_filter = ["billing_status"]
    list_per_page = 20
    search_fields = ["order_key", "full_name"]
    inlines = [OrderItemInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "percentage", "max_amount", "is_active"]
    list_filter = ["code", "percentage"]
    list_per_page = 10
    search_fields = ["code"]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ["order", "email", "accepted"]
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        if obj.accepted:
            if obj.orderItem.order_status == "Cancelled":
                if obj.order.payment_option == "razorpay":
                    payment_id = obj.order.payment_id
                    amount = str(int(obj.orderItem.price))
                    res = initate_refund_razorpay(payment_id, amount)
                    if res:
                        order_items = OrderItem.objects.get(id=obj.orderItem.id)
                        order_items.refund_granted = True
                        order_items.save()
                        notify.send(
                            request.user,
                            recipient=obj.order.user.user,
                            verb=f"Your refund is initated with razorpayid {res['id']}",
                        )
                    else:
                        notify.send(
                            request.user,
                            recipient=obj.order.user.user,
                            verb=f"Sorry no refund",
                        )
        return super(RefundAdmin, self).save_model(request, obj, form, change)


# # Register your models here.
# admin.site.register(Order)
# # admin.site.register(OrderItem)
