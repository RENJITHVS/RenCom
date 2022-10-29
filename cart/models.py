from django.db import models
from customers.models import CustomerProfile
from datetime import datetime

from shop.models import Product


class Basket(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class BasketItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(blank=True, null=True)
    orginal_amount = models.FloatField(blank=True, null=True)
    delivery_price = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    color_code = models.CharField(max_length=100, blank=True, null=True)
    basket = models.ForeignKey("Basket", on_delete=models.CASCADE)

    def __str__(self):
        return self.product.title

    class Meta:
        order_with_respect_to = "basket"
