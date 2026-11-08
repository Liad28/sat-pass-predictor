"""Download, archive and load TLEs; check their age."""
from __future__ import annotations

import datetime as dt
import urllib.request
import warnings
from pathlib import Path

from skyfield.api import EarthSatellite, load

GP_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad}&FORMAT=TLE"
DEFAULT_MAX_AGE_DAYS = 3.0


class StaleTLEWarning(UserWarning):
    """The TLE epoch is far enough from the prediction time to degrade accuracy."""


def fetch_tle_text(norad_id: int, timeout: float = 15.0) -> str:
    """Return the raw 3-line TLE text for one NORAD ID from the CelesTrak GP API."""
    url = GP_URL.format(norad=int(norad_id))
    req = urllib.request.Request(url, headers={"User-Agent": "satpass/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("ascii").strip()
    # CelesTrak answers 200 with a plain-text message when the ID is unknown
    if not text.splitlines() or not text.splitlines()[-1].startswith("2 "):
        raise ValueError(f"No TLE returned for NORAD {norad_id}: {text[:80]!r}")
    return text


def parse_tle_text(text: str, ts=None) -> list[EarthSatellite]:
    """Parse 2-line or 3-line TLE text (one or more satellites) into EarthSatellite objects."""
    ts = ts or load.timescale()
    lines = [ln.rstrip() for ln in text.strip().splitlines() if ln.strip()]
    sats, name, i = [], None, 0
    while i < len(lines):
        if lines[i].startswith("1 ") and i + 1 < len(lines) and lines[i + 1].startswith("2 "):
            sats.append(EarthSatellite(lines[i], lines[i + 1], name, ts))
            name, i = None, i + 2
        else:
            name, i = lines[i].strip(), i + 1
    if not sats:
        raise ValueError("No valid TLE line pairs found")
    return sats


def archive_tle(text: str, norad_id: int, archive_dir: str | Path = "data/tle_archive",
                date: dt.date | None = None) -> Path:
    """Save TLE text as <archive_dir>/<NORAD>_<YYYY-MM-DD>.txt (overwrites same-day file)."""
    date = date or dt.datetime.now(dt.timezone.utc).date()
    path = Path(archive_dir) / f"{int(norad_id)}_{date.isoformat()}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="ascii")
    return path


def tle_age_days(sat: EarthSatellite, t) -> float:
    """Signed age in days: t minus TLE epoch. Negative means propagating backwards."""
    return float(t - sat.epoch)


def check_tle_age(sat: EarthSatellite, t, max_age_days: float = DEFAULT_MAX_AGE_DAYS) -> float:
    """Return the age; emit StaleTLEWarning if |age| exceeds max_age_days."""
    age = tle_age_days(sat, t)
    if abs(age) > max_age_days:
        warnings.warn(
            f"{sat.name or 'satellite'}: TLE is {age:+.1f} d from epoch "
            f"(limit {max_age_days} d); expect degraded accuracy",
            StaleTLEWarning, stacklevel=2,
        )
    return age


def get_satellite(norad_id: int, ts=None, archive_dir: str | Path | None = "data/tle_archive"):
    """Fetch, optionally archive, and load one satellite."""
    text = fetch_tle_text(norad_id)
    if archive_dir is not None:
        archive_tle(text, norad_id, archive_dir)
    return parse_tle_text(text, ts)[0]
