from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from customers.models import Address, CustomerProfile

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('full_name', 'phone', 'address_line',
                  'city', 'pincode', 'default',)


class AddressInlineBaseformset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(AddressInlineBaseformset, self).__init__(*args, **kwargs)
        



AddressFormSet = inlineformset_factory(CustomerProfile, Address, fields=(
    'full_name', 'phone', 'address_line', 'city', 'pincode',), extra=1, formset=AddressInlineBaseformset)