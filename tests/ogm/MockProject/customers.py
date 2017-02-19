from neoalchemy import Property, OneToManyRelation, ManyToManyRelation

from .graph import OGMTestClass


class Customer(OGMTestClass):
    username = Property()
    email = Property(primary_key=True)
    addresses = ManyToManyRelation('HAS_ADDRESS', restrict_types=('Address',),
                                   backref='customer')
    orders = OneToManyRelation('PLACED_ORDER', restrict_types=('Order',),
                               backref='customer')
