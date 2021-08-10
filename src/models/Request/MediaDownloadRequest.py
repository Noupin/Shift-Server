#pylint: disable=C0103, C0301
"""
The Media Download Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class MediaDownloadRequest:
    filename: str
    download: str

MediaDownloadRequestDescription = """The name of the file to \
request and whether or not to download the file."""
