import warnings
from pathlib import Path

import pytest
from skyfield.api import load

from satpass.tle import StaleTLEWarning, archive_tle, check_tle_age, parse_tle_text, tle_age_days

DATA = Path(__file__).parent / "data" / "iss_2014-01-20.txt"
ts = load.timescale()


@pytest.fixture
def iss():
    return parse_tle_text(DATA.read_text(), ts)[0]


def test_parse_name_and_id(iss):
    assert iss.name == "ISS (ZARYA)"
    assert iss.model.satnum == 25544


def test_epoch_parsing(iss):
    # epoch field 14020.93268519 -> 2014, day-of-year 20.93268519 -> 2014-01-20 22:23:04 UTC
    y, mo, d, h, mi, s = iss.epoch.utc
    assert (y, mo, d, h, mi) == (2014, 1, 20, 22, 23)
    assert s == pytest.approx(4.0, abs=0.5)


def test_age_sign(iss):
    assert tle_age_days(iss, iss.epoch + 2.0) == pytest.approx(2.0)
    assert tle_age_days(iss, iss.epoch - 1.0) == pytest.approx(-1.0)


def test_fresh_tle_no_warning(iss):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        check_tle_age(iss, iss.epoch + 1.0, max_age_days=3.0)


def test_stale_tle_warns(iss):
    with pytest.warns(StaleTLEWarning):
        check_tle_age(iss, iss.epoch + 10.0, max_age_days=3.0)


def test_archive_filename(tmp_path):
    import datetime as dt
    p = archive_tle(DATA.read_text(), 25544, tmp_path, date=dt.date(2026, 11, 6))
    assert p.name == "25544_2026-11-06.txt"
    assert p.read_text().startswith("ISS (ZARYA)")
