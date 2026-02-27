from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["payment_method"]
        widgets = {
            "payment_method": forms.Select(
                choices=[
                    ("GCASH", "GCash"),
                    ("BANK_TRANSFER", "Bank Transfer"),
                    ("CASH", "Cash"),
                ],
                attrs={"class": "form-control"},
            )
        }
