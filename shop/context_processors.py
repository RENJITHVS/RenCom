from .models import Product, BrandName


def featured_products_and_brands(request):
    """
      The context processor must return a dictionary.
    """
    featuredProducts = Product.products.filter(
        is_featured=True)  # query the featured products
    brands = BrandName.objects.exclude(parent=None)  # query the brands details
    if  request.user.is_anonymous:
      wishlist_num= 1
    elif request.user.role == "CUSTOMER":
      wishlist_num = Product.objects.filter(wishlist_user=request.user.customerprofile).count()
    else:
      wishlist_num= 1
    return {'fproducts': featuredProducts, 'brands': brands, 'wishlist_num': wishlist_num}
