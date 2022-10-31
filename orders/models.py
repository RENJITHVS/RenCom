from django.db import models
from customers.models import CustomerProfile
from vendors.models import VendorProfile
from shop.models import Product


# Order
status_choice = (
    ("In Process", "In Process"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Cancelled", "Cancelled"),
)


class Order(models.Model):

    """
     order data from carts are stored in this model 
    """

    user = models.ForeignKey(
        CustomerProfile, on_delete=models.CASCADE, related_name="order_user"
    )
    full_name = models.CharField(max_length=50)
    email = models.CharField(max_length=254, blank=True)
    address1 = models.CharField(max_length=250)
    address2 = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    order_key = models.CharField(max_length=200)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    payment_option = models.CharField(max_length=200, blank=True)
    billing_status = models.BooleanField(default=False)
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, blank=True, null=True
    )

    # vendors = models.ManyToManyField(VendorProfile, related_name='order_vendors',blank = True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return str(self.created)


class OrderItemManager(models.Manager):
    """
    order according to parent
    """

    def get_queryset(self):
        return super(OrderItemManager, self).get_queryset().order_by("-order__created")


class OrderItem(models.Model):
    """
    order data of each product is stored here once order is placed
    """
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    order_status = models.CharField(
        choices=status_choice, default="In process", max_length=150
    )
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    objects = OrderItemManager()

    def __str__(self):
        return str(self.id)


class CouponManager(models.Manager):
    """ 
    filter only acitve coupons
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    percentage = models.FloatField()
    max_amount = models.FloatField(verbose_name="Max amount")
    used_users = models.ManyToManyField(
        CustomerProfile, related_name="used_coupon", blank=True
    )
    is_active = models.BooleanField(default=True)
    objects = CouponManager()

    def __str__(self):
        return self.code


class Refund(models.Model):
    """
    Manage refunds  Here!
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    orderItem = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, null=True, blank=True
    )
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
