
from email.policy import default
from tabnanny import verbose
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File

from django.urls import reverse

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from customers.models import CustomerProfile

from vendors.models import VendorProfile
from django.template.defaultfilters import slugify
from django.utils.text import slugify
from random import randint

from django.db.models import Avg, Count

# Create your models here.


class Category(MPTTModel):
    """
    MPTT category for brand model

    """
    title = models.CharField(max_length=50)
    image = models.ImageField(blank=True, upload_to='brands/')
    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name='children', on_delete=models.CASCADE)
    slug = models.SlugField(null=False, unique=True)
    status = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class MPTTMeta:
        verbose_name_plural = 'Categories'
        order_insertion_by = ['title']

    def get_absolute_url(self):
        return reverse('shop:category_list', args=[self.slug])

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
        return Product.products.filter(brand__in=self.get_descendants(include_self=True)).count()

    def save(self, *args, **kwargs):
        self.image = self.make_thumbnail(self.image)
        super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class Color(models.Model):
    """ 
    Product Color
    """

    title = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Products Colors'

    # def color_bg(self):
    #     return mark_safe('<div style="width:30px; height:30px; background-color:%s"></div>' % (self.color_code))

    def __str__(self):
        return self.title

# Size


class Size(models.Model):
    """ 
    Product Size
    """
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Products  Sizes'

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
    brand = models.ForeignKey(
        Category, related_name='brand', on_delete=models.RESTRICT)
    created_by = models.ForeignKey(
        VendorProfile, on_delete=models.CASCADE, related_name='vendor')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        upload_to='product_images/', default='images/default-image.jpg')
    slug = models.SlugField(max_length=255,)
    price = models.DecimalField(
        verbose_name="Your Price", max_digits=8, decimal_places=2)
    mrp_price = models.DecimalField(verbose_name="MRP Price",
                                    max_digits=8, decimal_places=2, blank=True, null=True)
    delivery_charges = models.DecimalField(
        verbose_name="Delivery Charges", max_digits=6, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    approve = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(
        upload_to='product_images/', blank=True, null=True)
    wishlist_user = models.ManyToManyField(
        CustomerProfile, related_name="user_wishlist", blank=True)
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse('shop:product_details', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        extra = str(randint(1, 100))
        if self.slug == '':
            self.slug = slugify(self.title) + '-' + extra
        super(Product, self).save(*args, **kwargs)

    def avarege_review(self):
        reviews = ProductReview.objects.filter(
            product=self, is_active=True).aggregate(average=Avg('review_rating'))
        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        return avg

    def count_review(self):
        reviews = ProductReview.objects.filter(
            product=self, is_active=True).aggregate(count=Count(int('id')))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.save('name.jpg')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class ProductAttribute(models.Model):
    """
    The Product Variations 
    """
    product = models.ForeignKey(
        Product, related_name='attributes', on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name="Price",
                                max_digits=8, decimal_places=2, blank=True, null=True)
    in_stock = models.BooleanField(
        verbose_name="Product in stock", default=True)

    class Meta:
        verbose_name_plural = 'Product Attributes'

    # def __str__(self):
    #     return self.product.title


class ProductImage(models.Model):
    """
    The Product Image Table contain multiple image of the 
    same products
    """
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE, blank=True, null=True)

    image = models.ImageField(
        upload_to='product_images/', blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to='product_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.thumbnail = self.make_thumbnail(self.image)
        super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 250)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


# Product Review
RATING = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class ProductReview(models.Model):
    user = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField()
    review_rating = models.CharField(choices=RATING, max_length=150)
    created_at = models.DateTimeField(auto_now_add=True,)

    class Meta:
        verbose_name_plural = 'Reviews'

    def get_review_rating(self):
        return self.review_rating
