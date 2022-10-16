
from django import forms
import django_filters
from .models import Category, Product,  ProductAttribute, ProductReview

from crispy_forms.utils import render_crispy_form
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField
from django.core.exceptions import ValidationError
from mptt.forms import TreeNodeChoiceField
from django.forms import modelformset_factory
from django.forms.widgets import ClearableFileInput


class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label='', lookup_expr='icontains', widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Enter Your Product..', 'style': 'height:4rem'}))
    brand = django_filters.ModelChoiceFilter(label='', queryset=Category.objects.exclude(
        parent=None), widget=forms.widgets.Select(attrs={'class': 'form-control', 'placeholder': 'Hi-'}))
    # product_type = django_filters.ModelChoiceFilter(
    #     label='', queryset=ProductType.objects.all())
    price__gt = django_filters.NumberFilter(
        label='', field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(
        label='', field_name='price', lookup_expr='lt')

    class Meta:
        model = Product
        fields = ['title', 'brand',  'price']

    # def __init__(self, data):
    #     super(ProductFilter, self).__init__()
    #     self.fields['title'].value = data


class AddProductForm(forms.ModelForm):

    brand = TreeNodeChoiceField(queryset=Category.objects.all(),
                                level_indicator='---', required=True)
    description = SummernoteTextField()

    class Meta:
        model = Product
        exclude = ['created_by', 'slug', 'created', 'updated',
                   'thumbnail', 'wishlist_user', 'image', 'approve', "is_active"]

    def clean_brand(self):
        brand = self.cleaned_data['brand']
        if brand.is_leaf_node() == False:
            raise ValidationError("please select from a listed Brand")
        return brand


ProductVarationFormset = modelformset_factory(
    ProductAttribute,
    fields=('color', 'size', 'price', 'in_stock'),
    extra=1,
    # widgets={
    #     'color': forms.TextInput(
    #         attrs={
    #             'class': 'col',
    #             'placeholder': 'Enter Colour ',
    #             'labels': 'None'
    #         }
    #     ),
    #     'size': forms.TextInput(
    #         attrs={
    #             'class': 'col',
    #             'placeholder': 'Enter size',
    #             'labels': 'None'
    #         }
    #     ),
    #     'price': forms.NumberInput(
    #         attrs={
    #             'class': 'col',
    #             'placeholder': 'Enter size',
    #             'labels': 'None'
    #         }
    #     ),
    #     'in_stock': forms.CheckboxInput(
    #         attrs={
    #             'class': 'col',
    #             'labels': 'None'
    #         }
    #     )
    # }
)


class MyClearableFileInput(ClearableFileInput):
    initial_text = 'currently'
    input_text = 'change'
    clear_checkbox_label = 'clear'


class AddProductImagesForm(forms.ModelForm):

    image = forms.ImageField(label='Select Product Image',
                             required=True, widget=MyClearableFileInput)

    class Meta:
        model = Product
        fields = ['image', 'is_active']


# class AddReviewForm(forms.ModelForm):
#     class Meta:
#         model = ProductReview
#         fields = ['review_text', 'review_rating', 'rate']
