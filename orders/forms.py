from django import forms

from accounts.models import DeliveryProfile

from .models import Booking


class BookingForm(forms.ModelForm):
    delivery_profile = forms.ModelChoiceField(
        queryset=DeliveryProfile.objects.none(),
        required=True,
        empty_label="Select delivery profile",
    )

    class Meta:
        model = Booking
        fields = ["event_date", "event_time", "venue", "delivery_profile"]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "event_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "venue": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["delivery_profile"].widget.attrs.update({"class": "form-control"})
        if user is not None:
            self.fields["delivery_profile"].queryset = DeliveryProfile.objects.filter(user=user)
