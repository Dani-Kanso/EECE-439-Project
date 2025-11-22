from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import atan2, cos, radians, sin, sqrt
from typing import Iterable, List, Optional

from .models import Contact


@dataclass
class Recommendation:
    contact: Contact
    score: float
    distance_km: Optional[float]


class RecommendationEngine:
    """
    Simple scoring engine inspired by the Doctor recommendation system reference.
    It rewards specialty, proximity, affordability, and patient rating.
    """

    def recommend(
        self, contacts: Iterable[Contact], preferences: dict, limit: int = 10
    ) -> List[Recommendation]:
        results: List[Recommendation] = []
        pref_specialty = self._normalize(preferences.get("specialty"))
        pref_city = self._normalize(preferences.get("city"))
        pref_state = self._normalize(preferences.get("state"))
        pref_max_fee = self._to_decimal(preferences.get("max_fee"))
        pref_min_rating = self._to_decimal(preferences.get("min_rating"))
        pref_lat = self._to_float(preferences.get("user_latitude"))
        pref_lon = self._to_float(preferences.get("user_longitude"))
        pref_max_distance = self._to_float(preferences.get("max_distance_km"))

        for contact in contacts:
            distance_km = self._compute_distance(pref_lat, pref_lon, contact)
            if pref_max_distance is not None and distance_km is not None:
                if distance_km > pref_max_distance:
                    continue

            score = 0.0
            rating_value = self._to_float(contact.rating) or 0.0
            score += rating_value * 2

            tags_value = contact.tags if isinstance(contact.tags, list) else (contact.tags or [])
            tag_blob = ",".join(tags_value).lower() if tags_value else ""

            if pref_specialty:
                if pref_specialty in contact.specialty.lower():
                    score += 5
                elif tag_blob and pref_specialty in tag_blob:
                    score += 2

            if pref_city and pref_city == contact.city.lower():
                score += 3
            if pref_state and pref_state == contact.state.lower():
                score += 1.5

            fee = self._to_float(contact.consultation_fee) or 0.0
            if pref_max_fee is not None:
                if fee <= float(pref_max_fee):
                    score += 2
                else:
                    score -= 3  # penalize but don't drop entirely

            if pref_min_rating is not None and rating_value < float(pref_min_rating):
                continue

            experience_bonus = min(contact.experience_years / 2, 10)
            score += experience_bonus

            if distance_km is not None:
                score += max(0, 5 - distance_km / 20)

            results.append(Recommendation(contact=contact, score=round(score, 2), distance_km=distance_km))

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    @staticmethod
    def _normalize(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        return str(value).strip().lower()

    @staticmethod
    def _to_decimal(value):
        if value in (None, ""):
            return None
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @staticmethod
    def _to_float(value):
        if value in (None, ""):
            return None
        if isinstance(value, float):
            return value
        if isinstance(value, Decimal):
            return float(value)
        return float(value)

    @staticmethod
    def _compute_distance(lat: Optional[float], lon: Optional[float], contact: Contact) -> Optional[float]:
        if None in (lat, lon, contact.latitude, contact.longitude):
            return None
        lat1 = radians(float(lat))
        lon1 = radians(float(lon))
        lat2 = radians(float(contact.latitude))
        lon2 = radians(float(contact.longitude))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return round(6371 * c, 2)  # Earth's radius in km
