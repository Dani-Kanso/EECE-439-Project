import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from contacts.models import Contact


class Command(BaseCommand):
    help = "Synchronize the doctor contact dataset into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete all existing contacts before importing the dataset.",
        )

    def handle(self, *args, **options):
        dataset_path = Path(__file__).resolve().parents[2] / "data" / "doctor_contacts.json"
        if not dataset_path.exists():
            self.stderr.write(f"Dataset not found at {dataset_path}")
            return

        with dataset_path.open(encoding="utf-8") as fp:
            records = json.load(fp)

        if not isinstance(records, list):
            self.stderr.write("Dataset format invalid. Expected a list of objects.")
            return

        with transaction.atomic():
            if options["replace"]:
                Contact.objects.all().delete()

            for entry in records:
                name = entry.get("name")
                city = entry.get("city")
                if not (name and city):
                    self.stderr.write("Skipping entry missing required fields: name/city")
                    continue

                defaults = {
                    "specialty": entry.get("specialty", ""),
                    "hospital": entry.get("hospital", ""),
                    "state": entry.get("state", ""),
                    "country": entry.get("country", "USA"),
                    "address": entry.get("address", ""),
                    "email": entry.get("email", ""),
                    "phone": entry.get("phone", ""),
                    "consultation_fee": self._decimal(entry.get("consultation_fee", 0)),
                    "rating": self._decimal(entry.get("rating", 0)),
                    "experience_years": entry.get("experience_years", 0),
                    "latitude": entry.get("latitude"),
                    "longitude": entry.get("longitude"),
                    "accepts_new_patients": entry.get("accepts_new_patients", True),
                    "tags": entry.get("tags", []),
                }

                Contact.objects.update_or_create(
                    name=name,
                    city=city,
                    defaults=defaults,
                )

        self.stdout.write(self.style.SUCCESS(f"Synchronized {len(records)} contacts."))

    @staticmethod
    def _decimal(value):
        if value in (None, ""):
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
