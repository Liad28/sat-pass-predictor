"""Ground-station geometry: topocentric look angles (alt/az/range)."""

from __future__ import annotations

import numpy as np
from skyfield.api import EarthSatellite, wgs84
from skyfield.timelib import Time, Timescale
from skyfield.toposlib import GeographicPosition


def make_station(lat_deg: float, lon_deg: float, elevation_m: float = 0.0) -> GeographicPosition:
    """Ground station on the WGS84 ellipsoid (geodetic lat/lon in deg, height in m)."""
    return wgs84.latlon(lat_deg, lon_deg, elevation_m=elevation_m)


def time_grid(ts: Timescale, start: Time, hours: float = 24.0, step_s: float = 60.0) -> Time:
    """Uniform Time array from `start` covering `hours` (inclusive), step `step_s` seconds."""
    offsets_days = np.arange(0.0, hours * 3600.0 + step_s, step_s) / 86400.0
    return ts.tt_jd(start.tt + offsets_days)


def look_angles(
    sat: EarthSatellite, station: GeographicPosition, t: Time
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Geometric elevation [deg], azimuth [deg, 0-360), range [km]. No refraction."""
    topocentric = (sat - station).at(t)
    alt, az, distance = topocentric.altaz()
    return alt.degrees, az.degrees, distance.km