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


class EventPackageInquiryForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    celebration_type = forms.CharField(
        required=True,
        label="What type of Celebration are you having?",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    celebration_date = forms.DateField(
        required=True,
        label="When will you be having your celebration?",
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date"}),
    )
