#pylint: disable=C0103, C0301
"""
The Train Request Data Model for the Shift API
"""
__author__ = "Noupin"


class TrainRequest:
    shiftUUID: str
    usePTM: bool
    prebuiltShiftModel: str
    epochs: int
    trainType: str

    def __init__(self, shiftUUID, usePTM, prebuiltShiftModel, epochs, trainType):
        self.shiftUUID = shiftUUID
        self.usePTM = usePTM
        self.prebuiltShiftModel = prebuiltShiftModel
        self.epochs = epochs
        self.trainType = trainType
