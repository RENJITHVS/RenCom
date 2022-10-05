from django import forms
import django_filters
from .models import BrandName, Product, ProductType
from django.template.context_processors import csrf
from crispy_forms.utils import render_crispy_form



class ProductFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(label='', lookup_expr='icontains', widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Enter Your Product..', 'style': 'height:4rem'}))
    brand = django_filters.ModelChoiceFilter(label='', queryset=BrandName.objects.exclude(
        parent=None), widget=forms.widgets.Select(attrs={'class': 'form-control', 'placeholder': 'Hi-'}))
    product_type = django_filters.ModelChoiceFilter(
        label='', queryset=ProductType.objects.all())
    price__gt = django_filters.NumberFilter(
        label='', field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(
        label='', field_name='price', lookup_expr='lt')

    class Meta:
        model = Product
        fields = ['title', 'brand', 'product_type', 'price']

    # def __init__(self, data):
    #     super(ProductFilter, self).__init__()
    #     self.fields['title'].value = data
