from django.db import models
from decimal import Decimal

# Create your models here.
from django.conf import settings

from shop.models import Product
from orders.models import Coupon


class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if settings.CART_SESSION_ID not in request.session:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, qty, variation=None):
        """
        Adding and updating the users cart session data
        """
        product_id = str(product.id)

        if product_id in self.cart:
            self.cart[product_id]["qty"] = qty
        else:
            self.cart[product_id] = {"price": str(variation.price), "qty": qty, "delivery_price": str(product.delivery_charges), "orginal_amount":str(product.mrp_price), "color": str(variation.color), "color_code": str(variation.color.color_code)}

        self.save()

    def __iter__(self):
        """
        Collect the product_id in the session data to query the database
        and return products
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            item["delivery_price"] = Decimal(item["delivery_price"])
            item['orginal_amount'] = Decimal(item["orginal_amount"])
            yield item

    def __len__(self):
        """
        Get the cart data and count the qty of items
        """
        return sum(item["qty"] for item in self.cart.values())

    def update(self, product, qty):
        """
        Update values in session data
        """
        product_id = str(product)
        if product_id in self.cart:
            self.cart[product_id]["qty"] = qty
        self.save()

    # def add_coupon(self, coupon=None)
    def orginal_price(self):
        return sum(Decimal(item['orginal_amount'])* item["qty"] for item in self.cart.values())

    def get_subtotal_price(self):
        return sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())

    def get_shipping_cost(self):
        return sum(Decimal(item['delivery_price']) for item in self.cart.values())

    def get_coupon_amount(self):

        subtotal = self.get_subtotal_price() 
        try:
            code = self.session.get('coupon')
            print(type(code))
            coupon = Coupon.objects.get(code = code)
            print(coupon)
            discount = subtotal * Decimal(coupon.percentage)
            print(discount)
            if discount > Decimal(coupon.max_amount):
                return Decimal(coupon.max_amount)
            else:
                return Decimal(discount)
        except:
            return 0

    def get_total_price(self):

        subtotal = self.get_subtotal_price() 
       
        if 'coupon' in self.session:
            subtotal -= self.get_coupon_amount()

        total = subtotal + self.get_shipping_cost()
        return total

    def get_total_saved(self):
        return self.orginal_price() - self.get_total_price()

    def delete(self, product):
        """
        Delete item from session data
        """
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        # Remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True
