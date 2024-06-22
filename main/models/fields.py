from typing import Any
from django.db import models
import uuid

class UUIDField(models.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 32  ## UUID without hyphens is 32 character long
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        super().get_prep_value(value)
        if value and isinstance(value, uuid.UUID):
            return value.hex
        return value
    
    def from_db_value(self, value, expression, connection):
        if value and isinstance(value, str):
            return uuid.UUID(value)
        return value
    
    def to_python(self, value):
        if not value:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)