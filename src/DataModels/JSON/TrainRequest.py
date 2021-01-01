#pylint: disable=C0103, C0301
"""
The Train Request Data Model for the Shift API
"""
__author__ = "Noupin"


class TrainRequest:
    uuid: str
    usePTM: bool
    prebuiltShiftModel: str

    def __init__(self, uuid, usePTM, prebuiltShiftModel):
        self.uuid = uuid
        self.usePTM = usePTM
        self.prebuiltShiftModel = prebuiltShiftModel
