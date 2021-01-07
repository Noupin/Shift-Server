#pylint: disable=C0103, C0301
"""
The Inference Request Data Model for the Shift API
"""
__author__ = "Noupin"


class InferenceRequest:
    shiftUUID: str
    usePTM: bool
    prebuiltShiftModel: str

    def __init__(self, shiftUUID, usePTM, prebuiltShiftModel):
        self.shiftUUID = shiftUUID
        self.usePTM = usePTM
        self.prebuiltShiftModel = prebuiltShiftModel
