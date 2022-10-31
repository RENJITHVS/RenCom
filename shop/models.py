from decimal import Decimal
from tabnanny import verbose
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.forms import BooleanField
from datetime import datetime
from django.urls import reverse
from django.utils import timezone

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from customers.models import CustomerProfile

from vendors.models import VendorProfile
from django.template.defaultfilters import slugify
from django.utils.text import slugify
from random import randint

from django.db.models import Avg, Count

MARGIN = 0.10


# Create your models here.
class Category(MPTTModel):
    """
    MPTT category for brand model

    """

    title = models.CharField(max_length=50)
    image = models.ImageField(blank=True, upload_to="brands/")
    parent = TreeForeignKey(
        "self", blank=True, null=True, related_name="children", on_delete=models.CASCADE
    )
    slug = models.SlugField(null=False, unique=True)
    status = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class MPTTMeta:
        verbose_name_plural = "Categories"
        order_insertion_by = ["title"]

    # def get_absolute_url(self):
    #     return reverse("shop:category_list", args=[self.slug])

    # def get_slug_list(self):
    #     try:
    #         ancestors = self.get_ancestors(include_self=True)
    #     except:
    #         ancestors = []
    #     else:
    #         ancestors = [i.slug for i in ancestors]
    #         slugs = []
    #         for i in range(len(ancestors)):
    #             slugs.append('/'.join(ancestors[:i+1]))
    #         return slugs

    def get_recursive_product_count(self):
        return Product.products.filter(
            brand__in=self.get_descendants(include_self=True)
        ).count()

    def save(self, *args, **kwargs):
        self.image = self.make_thumbnail(self.image)
        super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class Color(models.Model):
    """
    Product Color
    """

    title = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Products Colors"

    # def color_bg(self):
    #     return mark_safe('<div style="width:30px; height:30px; background-color:%s"></div>' % (self.color_code))

    def __str__(self):
        return self.title


class ProductManager(models.Manager):
    """
    filter only active products
    """

    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)


class Product(models.Model):
    """
    This table contain details of all product
    """

    # product_type = models.ForeignKey(
    #     ProductType, related_name='type_name', on_delete=models.RESTRICT, blank=True,)
    brand = models.ForeignKey(Category, related_name="brand", on_delete=models.RESTRICT)
    created_by = models.ForeignKey(
        VendorProfile, on_delete=models.CASCADE, related_name="vendor"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        upload_to="product_images/", default="images/default-image.jpg"
    )
    slug = models.SlugField(
        max_length=255,
    )

    mrp_price = models.DecimalField(
        verbose_name="MRP Price", max_digits=8, decimal_places=2, blank=True, null=True
    )
    delivery_charges = models.DecimalField(
        verbose_name="Delivery Charges", max_digits=6, decimal_places=2, default=0.00
    )
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    approve = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(upload_to="product_images/", blank=True, null=True)
    wishlist_user = models.ManyToManyField(
        CustomerProfile, related_name="user_wishlist", blank=True
    )
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = "Products"
        ordering = ("-created",)

    def get_absolute_url(self):
        return reverse("shop:product_details", args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        extra = str(randint(1, 100))
        if self.slug == "":
            self.slug = slugify(self.title) + "-" + extra
        super(Product, self).save(*args, **kwargs)

    def get_avg_rating(self):
        reviews = ProductReview.objects.filter(product=self)
        count = len(reviews)
        if count < 1:
            return 0
        sum = 0
        for rvw in reviews:
            sum += int(rvw.review_rating)
        return int(sum / count)

    def count_review(self):
        reviews = ProductReview.objects.filter(product=self)
        count = len(reviews)
        if count < 1:
            return 0
        else:
            return count

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert("RGB")
        img.save("name.jpg")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail



# class ProductAttributeManager(models.Manager):
#     """
#     filter only active products attributes
#     """
#     def get_queryset(self):
#         return super(ProductManager, self).get_queryset().filter(in_stock=True)


class   ProductAttribute(models.Model):
    """
    The Product Variations
    """

    product = models.ForeignKey(
        Product,
        related_name="attributes",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    # size = models.ForeignKey(Size, on_delete=models.CASCADE)
    vendor_price = models.DecimalField(
        verbose_name="Vendor Price", max_digits=8, decimal_places=2, blank=True, null=True
    )
    price = models.DecimalField(
        verbose_name="Selling Price", max_digits=8, decimal_places=2, blank=True, null=True
    )
    in_stock = models.BooleanField(verbose_name="Product in stock", default=True)

    # objects= ProductAttributeManager()
    # product_attributes = models.Manager()

    class Meta:
        verbose_name_plural = "Product Attributes"


    # def __str__(self):
    #     return self.product.title

    def save(self, *args, **kwargs):
        if self.vendor_price:
            self.price = self.vendor_price + (self.vendor_price * Decimal(MARGIN))
        super().save(*args, **kwargs)

    @property
    def product_price(self):
        exclusive_product_offers = Offers.objects.filter(products = self.product).first()
        category_offers = Offers.objects.filter(category= self.product.brand).first()
        exclusive_offer_amount = 0
        product_offer_amount = 0

        if exclusive_product_offers is not None:
            deduction = self.price*(Decimal(exclusive_product_offers.offer_percentage))/100
            if exclusive_product_offers.max_offer_reduction >= deduction:
                exclusive_offer_amount =  self.price - deduction
            else:
                exclusive_offer_amount = self.price - exclusive_product_offers.max_offer_reduction

        if category_offers is not None:
            deduction = self.price*(Decimal(category_offers.offer_percentage))/100
            if category_offers.max_offer_reduction >= deduction:
                exclusive_offer_amount =  self.price - deduction
            else:
                exclusive_offer_amount = self.price - category_offers.max_offer_reduction

        if exclusive_offer_amount ==0 and product_offer_amount == 0:
            return self.price
        elif exclusive_offer_amount >= product_offer_amount:
            return exclusive_offer_amount
        else:
            return product_offer_amount     

    @property
    def offer_difference(self):
        if self.product.mrp_price != self.product_price:
            return 100 - int(self.product_price/self.product.mrp_price * 100)
        else:
            return None



class ProductImage(models.Model):
    """
    The Product Image Table contain multiple image of the
    same products
    """
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE, blank=True, null=True
    )

    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="product_images/", blank=True, null=True)

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 250)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


# Product Review
RATING = (
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5"),
)

class ProductReview(models.Model):
    """ users can add review of the products here!"""
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    review_text = models.TextField()
    review_rating = models.CharField(choices=RATING, max_length=150)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = "Reviews"

    def get_review_rating(self):
        return self.review_rating


class Banner(models.Model):

    """display images in the banner on front ends"""

    images = models.ImageField(upload_to="banner_images/")
    tag_line = models.CharField(max_length=200)
    is_mobile = models.BooleanField(default = False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.tag_line

class Offers(models.Model):

    """ use this to add offers to category and products """

    name = models.CharField(max_length = 200, verbose_name="Offer Name")
    priority = models.PositiveIntegerField(unique = True)
    category = models.ManyToManyField('Category', blank = True)
    products = models.ManyToManyField('Product', blank = True)
    offer_percentage= models.PositiveIntegerField()
    max_offer_reduction = models.DecimalField(verbose_name="max reduction amount", max_digits=8, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(null= True, blank = True) 
    end_date = models.DateField(null= True, blank = True)

    class Meta:
        ordering = ['-priority',]
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'

    def __str__(self):
        return self.name

    @property
    def offer_ends_in(self):
        date_format = "%m/%d/%Y"
        today = datetime.strptime(str(datetime.now().date()), date_format)
        start_date = datetime.strptime(str(self.start_date), date_format)
        end_date = datetime.strptime(str(self.end_date), date_format)
        if today - start_date > 0 and today - end_date < 0:
            return abs(today - end_date)
        else:
            return None

    @property
    def active(self):
        date_format = "%Y-%m-%d"
        today = datetime.strptime(str(datetime.now().date()), date_format)
        start_date = datetime.strptime(str(self.start_date), date_format)
        end_date = datetime.strptime(str(self.end_date), date_format)
        if start_date < today and today < end_date:
            return True
        return False


