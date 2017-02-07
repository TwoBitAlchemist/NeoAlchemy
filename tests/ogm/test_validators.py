"""Tests for type validators"""
import uuid

import pytest

from neoalchemy.validators import *


def test_date_validators():
    assert isodate('Mar 24, 1985') == '1985-03-24'
    assert isodate('03/24/1985') == '1985-03-24'
    assert isodate('1985-03-24') == '1985-03-24'
    assert isodate('3-24-85') == '1985-03-24'
    with pytest.raises(ValueError):
        isodate('chicken nugget')
    assert isodatetime('Mar 24, 1985 10:50 PM') == '1985-03-24T22:50:00'
    assert isodatetime('Mar 24, 1985 10:50 p.m.') == '1985-03-24T22:50:00'
    assert isodatetime('24 Mar, 1985 22:50') == '1985-03-24T22:50:00'
    with pytest.raises(ValueError):
        isodatetime('cat loaf')


def test_uuid_validator():
    assert UUID(uuid.uuid1())
    assert UUID(uuid.uuid4())
    with pytest.raises(ValueError):
        assert UUID('12345')


def test_varchar_validator():
    max5 = varchar(5)
    assert max5('hello') == 'hello'
    assert max5('hi') == 'hi'
    with pytest.raises(ValueError):
        assert max5('hello!')
    max3 = varchar(3)
    assert max3('hi') == 'hi'
    with pytest.raises(ValueError):
        assert max3('hello')


def test_IP_validators():
    assert IPv4('192.168.1.1') == '192.168.1.1'
    assert IPv4('0.0.0.0') == '0.0.0.0'
    with pytest.raises(ValueError):
        assert IPv4('123.456.789.000')
    assert IPv6('::1') == '::1'
    assert IPv6('::FFFF:123:456:789:000') == '::FFFF:123:456:789:000'
    assert IPv6('0:0:0:0:0:0:0:1') == '0:0:0:0:0:0:0:1'
    with pytest.raises(ValueError):
        assert IPv6('2345235:5923058209385:wtfisthis')
    assert IP('192.168.1.1') == '192.168.1.1'
    assert IP('0.0.0.0') == '0.0.0.0'
    assert IP('::1') == '::1'
    assert IP('::FFFF:123:456:789:000') == '::FFFF:123:456:789:000'
    assert IP('0:0:0:0:0:0:0:1') == '0:0:0:0:0:0:0:1'
    with pytest.raises(ValueError):
        assert IP('Good morning starshine the earth says hello')
