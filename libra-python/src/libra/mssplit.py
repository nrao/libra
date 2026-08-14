from . import mssplit2py


class MSSplit:
    def __init__(self,
                 MSNBuf="",
                 OutMSBuf="",
                 deepCopy=False,
                 fieldStr="",
                 timeStr="",
                 spwStr="",
                 baselineStr="",
                 uvdistStr="",
                 taqlStr="",
                 scanStr="",
                 arrayStr="",
                 polnStr="",
                 stateObsModeStr="",
                 observationStr=""):
        self.MSNBuf = MSNBuf
        self.OutMSBuf = OutMSBuf
        self.deepCopy = deepCopy
        self.fieldStr = fieldStr
        self.timeStr = timeStr
        self.spwStr = spwStr
        self.baselineStr = baselineStr
        self.uvdistStr = uvdistStr
        self.taqlStr = taqlStr
        self.scanStr = scanStr
        self.arrayStr = arrayStr
        self.polnStr = polnStr
        self.stateObsModeStr = stateObsModeStr
        self.observationStr = observationStr
        self._result = None

    def run(self):
        self._result = mssplit2py.mssplit(
            MSNBuf=self.MSNBuf,
            OutMSBuf=self.OutMSBuf,
            deepCopy=self.deepCopy,
            fieldStr=self.fieldStr,
            timeStr=self.timeStr,
            spwStr=self.spwStr,
            baselineStr=self.baselineStr,
            uvdistStr=self.uvdistStr,
            taqlStr=self.taqlStr,
            scanStr=self.scanStr,
            arrayStr=self.arrayStr,
            polnStr=self.polnStr,
            stateObsModeStr=self.stateObsModeStr,
            observationStr=self.observationStr,
        )
        return self

    def __repr__(self):
        return f"MSSplit(MSNBuf={self.MSNBuf!r}, OutMSBuf={self.OutMSBuf!r})"
