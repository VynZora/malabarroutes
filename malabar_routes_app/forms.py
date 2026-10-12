from django import forms

from .models import (
    Blog,
    Category,
    Destination,
    GalleryImage,
    Testimonial,
    TourPackage,
)


# ============================================================
# TOUR PACKAGE FORM
# ============================================================

class TourPackageForm(forms.ModelForm):

    class Meta:
        model = TourPackage

        fields = [
            "name",
            "description",
            "main_image",
            "duration",
            "price_from",
            
            "category",
            "highlights",
            "inclusions",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].widget.attrs.update({
            "list": "category-list",
            "placeholder": "e.g. South Kerala",
            "autocomplete": "off",
        })

    def clean_category(self):
        # collapse extra spaces: "South   Kerala " -> "South Kerala"
        return " ".join(self.cleaned_data.get("category", "").split())

    @property
    def category_options(self):
        return (
            TourPackage.objects.exclude(category="")
            .order_by("category")
            .values_list("category", flat=True)
            .distinct()
        )


# ============================================================
# DESTINATION FORM
# ============================================================
class DestinationForm(forms.ModelForm):

    class Meta:
        model = Destination

        fields = [
            "name",
            "description",
            "image",
            "location",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].required = True
        self.fields["location"].widget.attrs.update({
            "list": "location-list",
            "placeholder": "e.g. Kerala",
            "autocomplete": "off",
        })

    def clean_location(self):
        # collapse extra spaces: "South   India " -> "South India"
        return " ".join(self.cleaned_data.get("location", "").split())

    @property
    def location_options(self):
        return (
            Destination.objects.exclude(location="")
            .order_by("location")
            .values_list("location", flat=True)
            .distinct()
        )

# ============================================================
# BLOG FORM
# ============================================================

class BlogForm(forms.ModelForm):

    class Meta:
        model = Blog

        fields = [
            "title",
            "description",
            "image",
        ]


# ============================================================
# CATEGORY FORM
# ============================================================

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category

        fields = [
            "name",
        ]


# ============================================================
# GALLERY IMAGE FORM
# ============================================================

class GalleryImageForm(forms.ModelForm):

    class Meta:
        model = GalleryImage

        fields = [
            "category",
            "title",
            "image",
        ]


# ============================================================
# TESTIMONIAL FORM
# ============================================================

class TestimonialForm(forms.ModelForm):

    class Meta:
        model = Testimonial

        fields = [
            "name",
            "image",
            "review",
        ]


# ---- add to forms.py ----
from django import forms
from .models import Activity


class ActivityForm(forms.ModelForm):
    # Lets CKEditor hide the real <textarea> without the browser
    # complaining about a "required" field it can't focus.
    use_required_attribute = False

    class Meta:
        model = Activity
        fields = ["title", "image", "description", "order", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Experiences",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
            }),
            "order": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_description(self):
        value = (self.cleaned_data.get("description") or "").strip()
        if not value:
            raise forms.ValidationError("Description is required.")
        return value