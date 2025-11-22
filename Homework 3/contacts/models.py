from django.db import models


class Contact(models.Model):
    """
    Represents a medical professional sourced from a public contact list.
    The fields are modeled after the Doctor recommendation data set shared
    in lab instructions.
    """

    name = models.CharField(max_length=120, help_text="Doctor's full name")
    specialty = models.CharField(
        max_length=120,
        default="General Practice",
        help_text="Primary medical specialty",
    )
    hospital = models.CharField(max_length=150, blank=True, help_text="Hospital or clinic affiliation")
    city = models.CharField(
        max_length=80,
        default="Unknown",
        help_text="City where the doctor practices",
    )
    state = models.CharField(max_length=80, blank=True, help_text="State or province")
    country = models.CharField(max_length=80, default="USA", help_text="Country")
    address = models.TextField(blank=True, help_text="Full address for mapping and routing")
    email = models.EmailField(blank=True, help_text="Business email")
    phone = models.CharField(max_length=25, blank=True, help_text="Office contact number")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Average consultation fee (USD)")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Average patient rating /5")
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of experience")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude of the office")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude of the office")
    accepts_new_patients = models.BooleanField(default=True, help_text="Whether the doctor accepts new patients")
    tags = models.JSONField(default=list, blank=True, help_text="List of searchable tags (procedures, languages, etc.)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Medical Contact"
        verbose_name_plural = "Medical Contacts"

    def __str__(self):
        """String representation of the contact"""
        return f"{self.name} ({self.specialty}) - {self.city}"
