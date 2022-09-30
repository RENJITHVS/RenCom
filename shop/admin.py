from django.contrib import admin

from mptt.admin import DraggableMPTTAdmin
# Register your models here.
from .models import *

@admin.register(BrandName)
class BrandAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = BrandName.objects.add_related_count(
                qs,
                Product,
                'brand',
                'brands_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = BrandName.objects.add_related_count(qs,
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

admin.site.register(ProductSpecification)
admin.site.register(ProductType)

class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationValueInline,
    ]