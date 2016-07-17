import dateutil.parser
import uuid


def parse_date(date_str):
    try:
        return dateutil.parser.parse(str(date_str))
    except:
        raise ValueError("Cannot parse %s as date." %
                         date_str.__class__.__name__)


def valid_uuid(id_):
    if id_ is None:
        return
    return str(uuid.UUID(str(id_)))


def isodate(date_):
    if date_ is None:
        return

    fmt = '%Y-%m-%d'
    return parse_date(date_).date().isoformat()


def isodatetime(datetime_):
    if datetime_ is None:
        return

    return parse_date(datetime_).isoformat()
