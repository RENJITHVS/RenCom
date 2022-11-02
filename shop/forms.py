from django import forms
import django_filters
from .models import Category, Product, ProductAttribute, ProductImage, ProductReview

from crispy_forms.utils import render_crispy_form
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField
from django.core.exceptions import ValidationError
from mptt.forms import TreeNodeChoiceField
from django.forms import BaseFormSet, BaseModelFormSet, IntegerField, modelformset_factory
from django.forms.widgets import ClearableFileInput
from django.core.validators import MinLengthValidator
from django.contrib import messages

from decimal import Decimal

class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        label="",
        lookup_expr="icontains",
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Enter Your Product..", "style": "height:4rem"}
        ),
    )
    brand = django_filters.ModelChoiceFilter(
        label="",
        queryset=Category.objects.exclude(parent=None),
        widget=forms.widgets.Select(
            attrs={"class": "form-control", "placeholder": "Brands"}
        ),
    )
    mrp_price__gt = django_filters.NumberFilter(
        label="", field_name="mrp_price", lookup_expr="gt",
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Enter the range", "class": "form-control",}
        ),
    )
    mrp_price__lt = django_filters.NumberFilter(
        label="", field_name="mrp_price", lookup_expr="lt",
         widget=forms.widgets.TextInput(
            attrs={"placeholder": "Enter Your Product..", "class": "form-control",}
        ),
    )

    class Meta:
        model = Product
        fields = ["title", "brand", "mrp_price"]

    # def __init__(self, data):
    #     super(ProductFilter, self).__init__()
    #     self.fields['title'].value = data


class AddProductForm(forms.ModelForm):

    brand = TreeNodeChoiceField(
        queryset=Category.objects.all(), level_indicator="---", required=True
    )
    title = forms.CharField(
        validators=[
            MinLengthValidator(20, "the field must contain at least 20 characters")
        ]
    )
    description = forms.Textarea()
    mrp_price = forms.FloatField(
        min_value=10, help_text="please enter actual MRP price of the product"
    )
    delivery_charges = forms.FloatField(
        min_value=0, help_text="provid '0.0' if no delievery charge"
    )
    # description = SummernoteTextFormField()

    class Meta:
        model = Product
        exclude = [
            "created_by",
            "slug",
            "created",
            "updated",
            "thumbnail",
            "wishlist_user",
            "image",
            "approve",
            "is_active",
        ]

    def clean_brand(self):
        brand = self.cleaned_data["brand"]
        if brand.is_leaf_node() == False:
            raise ValidationError("please select from a listed Brand")
        return brand

    def clean_description(self):
        brand = self.cleaned_data["description"]
        if len(brand) <= 50:
            raise ValidationError("please Add more than 20 words")
        return brand


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ("color", "vendor_price", "in_stock", "price")

    def __init__(self, *args,**kwargs):
        self.mrp = kwargs.pop('mrp')
        super(ProductAttributeForm, self).__init__(*args, **kwargs)
        self.fields['price'].disabled = True
        

    def clean_vendor_price(self):
        # custom validation for the name field
        vendor_price = float(self.cleaned_data['vendor_price'])
        total = vendor_price * .10 + vendor_price
        if total >= self.mrp:
            raise ValidationError(f"currently price of the product is {total}, price must be less than MRP price {self.mrp}")
        return vendor_price



ProductVarationFormset = modelformset_factory(ProductAttribute,form = ProductAttributeForm,
    extra=1,
)



ProductImageFormset = modelformset_factory(
    ProductImage,
    fields=("image",),
    extra=1,
)


class MyClearableFileInput(ClearableFileInput):
    initial_text = "currently"
    input_text = "change"
    clear_checkbox_label = "clear"


class AddProductImagesForm(forms.ModelForm):

    image = forms.ImageField(
        label="Select Product Image", required=True, widget=MyClearableFileInput
    )

    class Meta:
        model = Product
        fields = ["image", "is_active"]


# class AddReviewForm(forms.ModelForm):
#     class Meta:
#         model = ProductReview
#         fields = ['review_text', 'review_rating', 'rate']
