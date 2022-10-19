from django.contrib import admin

from mptt.admin import DraggableMPTTAdmin
# Register your models here.
from .models import *
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Category)
class BrandAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
            qs,
            Product,
            'brand',
            'brands_cumulative_count',
            cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                                                 Product,
                                                 'brand',
                                                 'brands_count',
                                                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.brands_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.brands_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


admin.site.register(Color)
# admin.site.register(Size)



class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute

class ProductImageInline(admin.TabularInline):
    model = ProductImage

@admin.register(Product)
class ProductAdmin(SummernoteModelAdmin):
    inlines = [
        ProductAttributeInline,
        ProductImageInline
    ]
    summernote_fields = ('description',)
    list_display = ('title', 'brand',)


# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
#     prepopulated_fields = {'slug': ('product_name',)}

# class VariationAdmin(admin.ModelAdmin):
#     list_display = ('product', 'variation_category', 'variation_value', 'is_active')
#     list_editable = ('is_active',)
#     list_filter = ('product', 'variation_category', 'variation_value')