from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from phonenumber_field.formfields import PhoneNumberField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Address, CustomerProfile, User
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.password_validation import validate_password


class RegistrationForm(forms.ModelForm):

    full_name = forms.CharField(max_length=200)
    email = forms.EmailField(
        max_length=100, error_messages={"required": "Sorry, you will need an email"}
    )
    # phone = PhoneNumberField(region="IN",required=False)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, validators=[validate_password]
    )
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.fields["full_name"].widget.attrs.update(
            {
                "class": "form-control-lg mb-3",
                "placeholder": "Enter Name",
                "name": "full_name",
                "id": "id_name",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control-lg mb-3",
                "placeholder": "Enter E-mail",
                "name": "email",
                "id": "id_email",
            }
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control-lg mb-3", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control-lg", "placeholder": "Repeat Password"}
        )

    def clean(self):

        cleaned_data = super().clean()
        email = cleaned_data.get("email").lower()
        full_name = cleaned_data.get("full_name").lower()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        res = all(c.isalpha() or c == " " for c in full_name)

        if not res:
            raise forms.ValidationError(
                "Don't use number or special character on your name"
            )
        elif User.objects.filter(email=email, email_verified=False).exists():
            raise forms.ValidationError(
                "User is already registerd, Please check your Inbox for activation link"
            )
        elif password != password2:
            raise forms.ValidationError("password and confirm password does not match")


class UserLoginForm(AuthenticationForm):

    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control-lg mb-3",
                "placeholder": "Enter Email",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control-lg",
                "placeholder": "Password",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Email",
                "id": "form-email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        u = User.objects.filter(email=email)
        if not u:
            raise forms.ValidationError(
                "Unfortunatley we can not find that email address"
            )
        return email


class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "New Password",
                "id": "form-newpass",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Repeat Password",
                "id": "form-new-pass2",
            }
        ),
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "full_name",
        ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["profile_pic", "account_number", "ifsc_code", "account_name"]
