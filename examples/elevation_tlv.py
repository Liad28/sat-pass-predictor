"""ISS elevation over Tel Aviv for the next 24 h."""

from pathlib import Path

import matplotlib.pyplot as plt
from skyfield.api import load

from satpass.geometry import look_angles, make_station, time_grid
from satpass.tle import check_tle_age, get_satellite

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "tle_archive"
ISS = 25544
TLV = (32.0853, 34.7818, 20.0)  # lat [deg], lon [deg], height [m]

ts = load.timescale()
sat = get_satellite(ISS, ts, ARCHIVE)
t0 = ts.now()
check_tle_age(sat, t0)

station = make_station(*TLV)
t = time_grid(ts, t0, hours=24, step_s=30)
el, az, rng = look_angles(sat, station, t)

hours = (t.tt - t0.tt) * 24.0
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(hours, el, lw=1)
ax.axhline(0, color="k", lw=0.8)
ax.axhline(10, color="r", ls="--", lw=0.8, label="min-el 10°")
ax.set_xlabel(f"hours since {t0.utc_strftime('%Y-%m-%d %H:%M')} UTC")
ax.set_ylabel("elevation [deg]")
ax.set_title(f"{sat.name} over Tel Aviv")
ax.set_ylim(-90, 90)
ax.legend()
fig.tight_layout()
fig.savefig(ROOT / "docs" / "elevation_iss_tlv.png", dpi=150)
plt.show()