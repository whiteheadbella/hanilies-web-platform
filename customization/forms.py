from django import forms
from .models import Customization

class CustomizationForm(forms.ModelForm):
    class Meta:
        model = Customization
        fields = [
            "cake",
            "size",
            "layers",
            "quantity",   # NEW
            "flavor",
            "theme",
            "message",
            "add_ons",
            "reference_image",
        ]

        widgets = {
            "add_ons": forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["add_ons"].queryset = self.fields["add_ons"].queryset.select_related("category").order_by(
            "category__name", "name"
        )

        for field_name, field in self.fields.items():
            if field_name != "add_ons":
                field.widget.attrs.update({"class": "form-control"})
