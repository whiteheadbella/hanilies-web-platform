from django import forms

from .models import GalleryPhoto


class GalleryPhotoForm(forms.ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = ["title", "image", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class HomeHeroUploadForm(forms.Form):
    title = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control",
                   "placeholder": "Image title (optional)"}
        ),
    )
    image = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )
