import string
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import User
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm)



class RegistrationForm(forms.ModelForm):

    full_name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=100, error_messages={
        'required': 'Sorry, you will need an email'})
    # phone = PhoneNumberField(region="IN",required=False)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)
    
    def clean_full_name(self):
        full_name = self.cleaned_data['full_name'].lower()
        res =  all(c.isalpha() or c==" " for c in full_name)
        if not res:
            raise forms.ValidationError(
                "Don't use number or special character on your name")
        return full_name

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError(
                'This Email is already taken')
        return email

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

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
        attrs={'class': 'form-control-lg mb-3', 'placeholder': 'Enter Email',}))
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
        
