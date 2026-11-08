"""Where is the ISS right now? Position, altitude and sub-satellite point."""
from skyfield.api import load, wgs84

from satpass.tle import check_tle_age, get_satellite

ts = load.timescale()
iss = get_satellite(25544, ts)
t = ts.now()

age = check_tle_age(iss, t)
geocentric = iss.at(t)                       # GCRS position (km), from SGP4 TEME output
sub = wgs84.subpoint_of(geocentric)          # geodetic lat/lon of the point below
height = wgs84.height_of(geocentric)         # height above the WGS84 ellipsoid

print(f"{iss.name}  epoch {iss.epoch.utc_iso()}  age {age:+.2f} d")
print(f"time      {t.utc_iso()}")
print(f"lat/lon   {sub.latitude.degrees:+.3f}, {sub.longitude.degrees:+.3f} deg")
print(f"altitude  {height.km:.1f} km")
print(f"|r|       {(geocentric.position.km**2).sum()**0.5:.1f} km")
