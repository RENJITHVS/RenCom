from django import forms
from .models import Refund


class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = (
            "email",
            "reason",
        )
