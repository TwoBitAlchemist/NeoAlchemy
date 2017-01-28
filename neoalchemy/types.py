import dateutil.parser
import socket
import uuid


def IPv4(ip_addr):
    """
    Validate a string as an IPv4 address. See `man 3 inet` for details.
    """
    ip_addr = str(ip_addr)

    try:
        socket.inet_aton(ip_addr)
    except socket.error:
        raise ValueError('Invalid IPv4 address: %s' % ip_addr)

    return ip_addr


def IPv6(ip_addr):
    """
    Validate a string as an IPv6 address. See `man 3 inet_pton` for details.

    Availability is platform-dependent.
    """
    ip_addr = str(ip_addr)

    try:
        socket.inet_pton(socket.AF_INET6, ip_addr)
    except socket.error:
        raise ValueError('Invalid IPv6 address: %s' % ip_addr)
    except AttributeError:
        raise ValueError('IPv6 validation unavailable on this platform.')

    return ip_addr


def IP(ip_addr):
    """
    Validate an IP address. Tries IPv4 validation and falls back to IPv6
    on error.

    Availability of IPv6 validation is platform-dependent.
    """
    try:
        return IPv4(ip_addr)
    except ValueError:
        return IPv6(ip_addr)


def _parse_date(date_str):
    try:
        return dateutil.parser.parse(str(date_str))
    except:
        raise ValueError("Cannot parse %s as date." %
                         date_str.__class__.__name__)


def isodate(date_):
    """
    Fuzzy parse a date and return an ISO-8601 formatted date.
    """
    if date_ is None:
        return

    return _parse_date(date_).date().isoformat()


def isodatetime(datetime_):
    """
    Fuzzy parse a date and return an ISO-8601 formatted datetime.
    """
    if datetime_ is None:
        return

    return _parse_date(datetime_).isoformat()


def UUID(id_):
    """
    Validator for a valid UUID. Relies on Python's uuid.UUID validator.
    """
    if id_ is None:
        return

    return str(uuid.UUID(str(id_)))


def varchar(length):
    """
    Factory for a character length validator of the specified length.
    """
    length = int(length)

    def char_length_validator(string):
        """
        Validate a string ensuring that it doesn't exceed a maximum length.
        """
        if string is None:
            return

        string = str(string)
        if len(string) > length:
            raise ValueError("Value '%s' exceeds character limit "
                             "of %i." % (string, length))
        return string

    return char_length_validator
