from django import forms

from accounts.models import DeliveryProfile

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["event_date", "event_time", "venue", "delivery_address"]
        labels = {
            "delivery_address": "Delivery Address",
        }
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "event_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "venue": forms.TextInput(attrs={"class": "form-control"}),
            "delivery_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter delivery address",
                    "autocomplete": "street-address",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.delivery_address_autofilled = False
        if user is not None and not self.is_bound and not self.initial.get("delivery_address"):
            profile = (
                DeliveryProfile.objects.filter(user=user)
                .order_by("-is_default", "-created_at")
                .first()
            )
            if profile:
                saved_address = ", ".join(
                    part
                    for part in [
                        profile.house_no,
                        profile.street,
                        profile.barangay,
                        profile.city,
                        profile.province,
                    ]
                    if part
                )
                self.fields["delivery_address"].initial = saved_address
                self.initial["delivery_address"] = saved_address
                self.delivery_address_autofilled = True
