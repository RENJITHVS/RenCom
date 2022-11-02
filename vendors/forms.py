from django import forms
from django.forms import ModelForm
import razorpay
from customers.models import User
from .models import VendorProfile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name",
        ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = [
            "profile_pic",
            "address1",
            "address2",
            "city",
            "phone",
            "pincode",
            "account_number",
            "ifsc_code",
            "razorpay_id",
            "account_name",
            "document",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["address1"].required = True
        self.fields["city"].required = True
        self.fields["phone"].required = True
        self.fields["pincode"].required = True
        self.fields["account_number"].required = True
        self.fields["ifsc_code"].required = True
        self.fields["document"].required = True

class RazorpayForm(forms.ModelForm):
    def clean(self):
        razorpay_id = self.cleaned_data['razorpay_id']
        if not razorpay_id:
            raise forms.ValidationError({'razorpay_id':'please provide razorpay id for fund transfer'})