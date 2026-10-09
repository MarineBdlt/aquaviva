"""Tarification flexible : jours, semaines, mois (nuits pendant la période)."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Any

from booking_engine.models import Apartment, ApartmentSeasonRate


def load_apartment_season_rates(apartment_id: int):
    return (
        ApartmentSeasonRate.query.filter_by(apartment_id=apartment_id)
        .order_by(ApartmentSeasonRate.start_date.asc())
        .all()
    )


def _match_season_rate(season_rates, day: date):
    matches = [s for s in season_rates if s.start_date <= day <= s.end_date]
    if not matches:
        return None
    # Plus courte période = tarif le plus spécifique
    return min(matches, key=lambda s: ((s.end_date - s.start_date).days, s.id))


def get_apartment_rate_for_date(apartment, day, season_rates=None):
    """Effective nightly rate for a calendar day (season or default)."""
    from datetime import datetime as dt

    if isinstance(day, dt):
        day = day.date()
    if season_rates is None:
        season_rates = load_apartment_season_rates(apartment.id)
    season = _match_season_rate(season_rates, day)
    if season:
        return season.rate, "season", season
    return apartment.rate, "default", None


def get_apartment_rate_for_month(apartment, year: int, month: int, season_rates=None):
    """Effective nightly rate shown for a month (uses the 15th when possible)."""
    last = monthrange(year, month)[1]
    mid_day = date(year, month, min(15, last))
    rate, source, _ = get_apartment_rate_for_date(
        apartment, mid_day, season_rates=season_rates
    )
    return rate, source


def add_months(start: date, months: int) -> date:
    if months < 0:
        raise ValueError("months must be >= 0")
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    day = min(start.day, monthrange(year, month)[1])
    return date(year, month, day)


def period_end(start: date, unit: str, quantity: int) -> date:
    """Return exclusive end date (checkout) for the stay."""
    qty = max(1, int(quantity))
    unit = (unit or "days").lower()
    if unit in ("day", "days", "nuit", "nuits", "d"):
        return start + timedelta(days=qty)
    if unit in ("week", "weeks", "semaine", "semaines", "w"):
        return start + timedelta(days=qty * 7)
    if unit in ("month", "months", "mois", "m"):
        return add_months(start, qty)
    raise ValueError(f"unité inconnue: {unit}")


def nights_between(start: date, end: date) -> int:
    return max(0, (end - start).days)


def quote_apartment(
    apartment: Apartment,
    start: date,
    unit: str = "days",
    quantity: int = 1,
) -> dict[str, Any]:
    """Estimate total price for a stay using nightly + season rates."""
    end = period_end(start, unit, quantity)
    nights = nights_between(start, end)
    if nights < 1:
        return {
            "ok": False,
            "error": "invalid_period",
            "apartment_id": apartment.id,
            "apartment_name": apartment.name,
        }

    season_rates = load_apartment_season_rates(apartment.id)
    total = 0
    night_rates: list[dict[str, Any]] = []
    day = start
    while day < end:
        rate, source, season = get_apartment_rate_for_date(
            apartment, day, season_rates=season_rates
        )
        total += int(rate)
        night_rates.append(
            {
                "date": day.isoformat(),
                "rate": int(rate),
                "source": source,
                "label": getattr(season, "label", None) if season else None,
            }
        )
        day += timedelta(days=1)

    avg = round(total / nights) if nights else 0
    return {
        "ok": True,
        "apartment_id": apartment.id,
        "apartment_name": apartment.name,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "nights": nights,
        "unit": unit,
        "quantity": int(quantity),
        "total": total,
        "avg_night": avg,
        "currency": "EUR",
        "breakdown_sample": night_rates[:14],
    }


def current_season_offers(
    today: date | None = None, horizon_days: int = 180
) -> list[dict[str, Any]]:
    """Active or upcoming season offers to highlight on the homepage."""
    today = today or date.today()
    horizon = today + timedelta(days=horizon_days)
    offers: list[dict[str, Any]] = []
    apartments = Apartment.query.order_by(Apartment.name.asc()).all()
    for apt in apartments:
        seasons = load_apartment_season_rates(apt.id)
        for season in seasons:
            if season.end_date < today:
                continue
            if season.start_date > horizon:
                continue
            active = season.start_date <= today <= season.end_date
            offers.append(
                {
                    "apartment_id": apt.id,
                    "apartment_name": apt.name,
                    "bedrooms": apt.bedrooms,
                    "image": apt.images[0].image_file if apt.images else None,
                    "default_rate": apt.rate,
                    "rate": season.rate,
                    "label": season.label or "",
                    "start": season.start_date.isoformat(),
                    "end": season.end_date.isoformat(),
                    "active": active,
                    "week_from": season.rate * 7,
                    "month_from": season.rate * 30,
                }
            )
    offers.sort(key=lambda o: (not o["active"], o["start"], o["rate"]))
    if offers:
        return offers

    # Fallback : mettre en avant les tarifs de base des appartements
    for apt in apartments:
        offers.append(
            {
                "apartment_id": apt.id,
                "apartment_name": apt.name,
                "bedrooms": apt.bedrooms,
                "image": apt.images[0].image_file if apt.images else None,
                "default_rate": apt.rate,
                "rate": apt.rate,
                "label": "",
                "start": today.isoformat(),
                "end": (today + timedelta(days=365)).isoformat(),
                "active": True,
                "week_from": apt.rate * 7,
                "month_from": apt.rate * 30,
            }
        )
    return offers
