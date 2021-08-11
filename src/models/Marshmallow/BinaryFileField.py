#pylint: disable=C0103, C0301
"""
The Marshmallow Binary File Field for a shift
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields

#First Party Imports
from src.config import marshmallowPlugin


@marshmallowPlugin.map_to_openapi_type('string', None)
class BinaryFileField(fields.Raw):
    pass
