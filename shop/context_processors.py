from .models import Product, BrandName


def featured_products_and_brands(request):
    """
      The context processor must return a dictionary.
    """
    featuredProducts = Product.products.filter(
        is_featured=True)  # query the featured products
    brands = BrandName.objects.exclude(parent=None)  # query the brands details
    return {'fproducts': featuredProducts, 'brands': brands}
