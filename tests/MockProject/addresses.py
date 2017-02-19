from neoalchemy import Property

from .graph import OGMTestClass


class Address(OGMTestClass):
    street_level = Property()
    city = Property()


class DomesticAddress(Address):
    state = Property()
    zip_code = Property()


class InternationalAddress(Address):
    postal_code = Property()
