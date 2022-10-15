import string
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Address, CustomerProfile, User
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth.password_validation import validate_password


class RegistrationForm(forms.ModelForm):

    full_name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=100, error_messages={
        'required': 'Sorry, you will need an email'})
    # phone = PhoneNumberField(region="IN",required=False)
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput, validators=[validate_password])
    password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean(self):

        cleaned_data = super(RegistrationForm, self).clean()
        email = cleaned_data.get('email').lower()
        full_name = cleaned_data.get('full_name').lower()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        res = all(c.isalpha() or c == " " for c in full_name)

        if not res:
            raise forms.ValidationError(
                "Don't use number or special character on your name")
        elif User.objects.filter(email=email, email_verified=False).exists():
            raise forms.ValidationError(
                'User is already registerd, Please check your Inbox for activation link')
        elif User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(
                'This Email is already taken')
        elif password != password2:
            raise forms.ValidationError(
                "password and confirm password does not match"
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields['full_name'].widget.attrs.update(
            {'class': 'form-control-lg mb-3', 'placeholder': 'Enter Name', 'name': 'full_name', 'id': 'id_name'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control-lg mb-3', 'placeholder': 'Enter E-mail', 'name': 'email', 'id': 'id_email'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control-lg mb-3', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control-lg', 'placeholder': 'Repeat Password'})


class UserLoginForm(AuthenticationForm):

    email = forms.CharField(widget=forms.EmailInput(
        attrs={'class': 'form-control-lg mb-3', 'placeholder': 'Enter Email', }))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control-lg',
            'placeholder': 'Password',
        }
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('full_name', 'phone', 'address_line',
                  'city', 'pincode', 'default',)


class AddressInlineBaseformset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(AddressInlineBaseformset, self).__init__(*args, **kwargs)
        default_address = False
        for form in self.forms:
            if form.fields['default'].initial == True:
                default_address = True
        if not default_address:
            self.forms[0].fields['default'].initial = True


AddressFormSet = inlineformset_factory(CustomerProfile, Address, fields=(
    'full_name', 'phone', 'address_line', 'city', 'pincode', 'default',), extra=1, formset=AddressInlineBaseformset)
