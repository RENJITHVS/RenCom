from .models import Category, Product


def featured_products_and_brands(request):
    """
    The context processor must return a dictionary.
    """
    featuredProducts = Product.products.filter(
        is_featured=True
    )  # query the featured products
    brands = Category.objects.exclude(parent=None)  # query the brands details
    parents = Category.objects.filter(parent=None)  # query the category
    tree_category = Category.objects.all()
    if request.user.is_anonymous:
        wishlist_num = 0
    elif request.user.role == "CUSTOMER" and request.user.customerprofile:
        wishlist_num = Product.objects.filter(
            wishlist_user=request.user.customerprofile
        ).count()
    else:
        wishlist_num = 0
    return {
        "fproducts": featuredProducts,
        "brands": brands,
        "wishlist_num": wishlist_num,
        "categories": parents,
        "tree_category": tree_category,
    }
