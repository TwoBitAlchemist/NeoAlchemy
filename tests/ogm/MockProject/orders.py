import uuid

from neoalchemy import Property
from neoalchemy.validators import UUID

from .graph import OGMTestClass


class Order(OGMTestClass):
    id = Property(type=UUID, default=uuid.uuid4, primary_key=True,
                  indexed=True)
