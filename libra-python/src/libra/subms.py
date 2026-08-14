from . import subms2py


class SubMS:
    def __init__(self,
                 MSNBuf="",
                 OutMSBuf="",
                 WhichColStr="data",
                 deepCopy=False,
                 fieldStr="*",
                 timeStr="",
                 spwStr="*",
                 baselineStr="",
                 scanStr="",
                 arrayStr="",
                 uvdistStr="",
                 taqlStr="",
                 integ=-1):
        self.MSNBuf = MSNBuf
        self.OutMSBuf = OutMSBuf
        self.WhichColStr = WhichColStr
        self.deepCopy = deepCopy
        self.fieldStr = fieldStr
        self.timeStr = timeStr
        self.spwStr = spwStr
        self.baselineStr = baselineStr
        self.scanStr = scanStr
        self.arrayStr = arrayStr
        self.uvdistStr = uvdistStr
        self.taqlStr = taqlStr
        self.integ = integ
        self._result = None

    def run(self):
        self._result = subms2py.subms(
            MSNBuf=self.MSNBuf,
            OutMSBuf=self.OutMSBuf,
            WhichColStr=self.WhichColStr,
            deepCopy=self.deepCopy,
            fieldStr=self.fieldStr,
            timeStr=self.timeStr,
            spwStr=self.spwStr,
            baselineStr=self.baselineStr,
            scanStr=self.scanStr,
            arrayStr=self.arrayStr,
            uvdistStr=self.uvdistStr,
            taqlStr=self.taqlStr,
            integ=self.integ,
        )
        return self

    def __repr__(self):
        return f"SubMS(MSNBuf={self.MSNBuf!r}, OutMSBuf={self.OutMSBuf!r}, WhichColStr={self.WhichColStr!r})"
