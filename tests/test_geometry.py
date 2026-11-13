from pathlib import Path

import numpy as np
import pytest
from skyfield.api import load

from satpass.geometry import look_angles, make_station, time_grid
from satpass.tle import parse_tle_text

DATA = Path(__file__).parent / "data" / "iss_2014-01-20.txt"
TLV = (32.0853, 34.7818, 20.0)  # lat [deg], lon [deg], height [m]


@pytest.fixture(scope="module")
def iss_tlv_24h():
    ts = load.timescale()
    sat = parse_tle_text(DATA.read_text(), ts)[0]
    station = make_station(*TLV)
    t = time_grid(ts, sat.epoch, hours=24, step_s=60)
    return look_angles(sat, station, t)


def test_elevation_range(iss_tlv_24h):
    el, _, _ = iss_tlv_24h
    assert np.all((el >= -90) & (el <= 90))


def test_azimuth_range(iss_tlv_24h):
    _, az, _ = iss_tlv_24h
    assert np.all((az >= 0) & (az < 360))


def test_range_physical(iss_tlv_24h):
    _, _, rng = iss_tlv_24h
    # min ~ orbit altitude (~415 km, overhead); max ~ R_E + r_orbit (~13,150 km, opposite side)
    assert np.all((rng > 300) & (rng < 13_500))

