
from django import forms
from customers.models import User
from .models import  VendorProfile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name',]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['profile_pic', 'address1', 'address2', 'city', 'phone', 'pincode','account_number', "ifsc_code", "account_name", 'document' ]
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address1'].required = True
        self.fields['city'].required = True
        self.fields['phone'].required = True
        self.fields['pincode'].required = True
        self.fields['account_number'].required = True
        self.fields['ifsc_code'].required = True
        self.fields['document'].required = True