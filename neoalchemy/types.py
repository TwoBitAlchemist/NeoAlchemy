from dateutil.parser import parse as parse_date
import uuid


def valid_uuid(id_):
    if id_ is None:
        return
    return str(uuid.UUID(str(id_)))


def isodate(date_):
    if date_ is None:
        return

    fmt = '%Y-%m-%d'
    return parse_date(str(date_)).date().isoformat()


def isodatetime(datetime_):
    if datetime_ is None:
        return

    return parse_date(str(datetime_)).isoformat()
