from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DeliveryProfile


class CustomerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Bootstrap styling
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class DeliveryProfileForm(forms.ModelForm):
    class Meta:
        model = DeliveryProfile
        fields = [
            "full_name",
            "phone",
            "house_no",
            "street",
            "barangay",
            "city",
            "province",
            "landmark",
            "is_default",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name == "is_default":
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})