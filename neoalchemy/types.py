from datetime import datetime
import uuid


def valid_uuid(id_):
    if id_ is None:
        return
    return str(uuid.UUID(str(id_)))


def isodate(date_str):
    if date_str is None:
        return
    return datetime.strptime(str(date_str), '%Y-%m-%d').date()
