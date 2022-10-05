
from django.db import models

from django.urls import reverse

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from customers.models import CustomerProfile

from vendors.models import VendorProfile
from django.template.defaultfilters import slugify

# Create your models here.


class BrandName(MPTTModel):
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
        order_insertion_by = ['title']

    # def get_absolute_url(self):
    #     return reverse('category_detail', kwargs={'slug': self.slug})


class ProductType(models.Model):
    """
    ProductType Table will provide a list of the different types
    of products that are for sale.
    """

    name = models.CharField(verbose_name="Product Name",
                            help_text="Required", max_length=255, unique=True)
    image = models.ImageField(
        upload_to='product_type_images/', default='images/default-image.jpg', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    """
    The Product Specification Table contains product
    specifiction or features for the product types.
    """

    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT)
    name = models.CharField(verbose_name="Name",
                            help_text="Required", max_length=255)

    class Meta:
        verbose_name = "Product Specification"
        verbose_name_plural = "Product Specifications"

    def __str__(self):
        return self.name


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
    product_type = models.ForeignKey(
        ProductType, related_name='type_name', on_delete=models.RESTRICT)
    brand = models.ForeignKey(
        BrandName, related_name='brand', on_delete=models.RESTRICT)
    created_by = models.ForeignKey(
        VendorProfile, on_delete=models.CASCADE, related_name='vendor')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='product_images/', default='default-image.jpg')
    slug = models.SlugField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default= False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    wishlist_user = models.ManyToManyField(CustomerProfile, related_name="user_wishlist", blank=True)
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',)


    def get_absolute_url(self):
        return reverse('shop:product_details', args=[self.slug])
    

    def __str__(self):
        return self.title


class ProductSpecificationValue(models.Model):
    """
    The Product Specification Value table holds each of the
    products individual specification or bespoke features.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.ForeignKey(
        ProductSpecification, on_delete=models.RESTRICT)
    value = models.CharField(
        verbose_name="value",
        help_text="Product specification value (maximum of 255 words",
        max_length=255,
    )

    class Meta:
        verbose_name = "Product Specification Value"
        verbose_name_plural = "Product Specification Values"

    def __str__(self):
        return self.value
