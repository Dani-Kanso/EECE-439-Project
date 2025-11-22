from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """Form used to create or update contacts sourced from the doctor dataset."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tags_value = self.initial.get("tags")
        if isinstance(tags_value, list):
            self.initial["tags"] = ", ".join(tags_value)
        elif self.instance and isinstance(self.instance.tags, list) and not tags_value:
            self.initial["tags"] = ", ".join(self.instance.tags)

    class Meta:
        model = Contact
        fields = [
            "name",
            "specialty",
            "hospital",
            "city",
            "state",
            "country",
            "address",
            "email",
            "phone",
            "consultation_fee",
            "rating",
            "experience_years",
            "latitude",
            "longitude",
            "accepts_new_patients",
            "tags",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "tags": forms.Textarea(attrs={"rows": 2, "placeholder": "Comma separated values e.g. knee surgery, telehealth"}),
            "consultation_fee": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "rating": forms.NumberInput(attrs={"step": "0.1", "min": "0", "max": "5"}),
            "experience_years": forms.NumberInput(attrs={"min": "0"}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001"}),
        }

    def clean_tags(self):
        """Normalize tags into a list."""
        tags = self.cleaned_data.get("tags", [])
        if isinstance(tags, list):
            return tags
        if not tags:
            return []
        return [tag.strip() for tag in str(tags).split(",") if tag.strip()]


class ContactSearchForm(forms.Form):
    """Filters rendered on the contacts list page."""

    query = forms.CharField(
        required=False,
        label="Keyword",
        widget=forms.TextInput(attrs={"placeholder": "Name, hospital or keyword"}),
    )
    specialty = forms.CharField(required=False, label="Specialty")
    city = forms.CharField(required=False, label="City")
    state = forms.CharField(required=False, label="State")
    max_fee = forms.DecimalField(required=False, min_value=0, label="Max Fee (USD)")
    min_rating = forms.DecimalField(required=False, min_value=0, max_value=5, label="Min Rating")
    accepts_new_patients = forms.BooleanField(required=False, label="Accepting new patients")
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ("name", "Name (A-Z)"),
            ("rating", "Highest Rated"),
            ("fee", "Lowest Fee"),
            ("experience", "Most Experienced"),
        ],
        initial="name",
        label="Sort By",
    )


class RecommendationForm(forms.Form):
    """Inputs collected for the recommendation engine."""

    specialty = forms.CharField(required=False, label="Specialty or procedure")
    city = forms.CharField(required=False, label="City preference")
    state = forms.CharField(required=False, label="State preference")
    max_fee = forms.DecimalField(required=False, min_value=0, label="Budget (USD)")
    min_rating = forms.DecimalField(required=False, min_value=0, max_value=5, label="Minimum rating")
    user_latitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        label="Your latitude",
        widget=forms.NumberInput(attrs={"step": "0.000001"}),
    )
    user_longitude = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        label="Your longitude",
        widget=forms.NumberInput(attrs={"step": "0.000001"}),
    )
    max_distance_km = forms.DecimalField(
        required=False,
        min_value=1,
        label="Max distance (km)",
        widget=forms.NumberInput(attrs={"step": "1"}),
    )
