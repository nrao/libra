from . import coyote2py


class Coyote:
    def __init__(self,
                 MSNBuf="",
                 telescopeName="",
                 NX=0,
                 cellSize=0.0,
                 stokes="",
                 refFreqStr="",
                 nW=1,
                 cfCacheName="",
                 WBAwp=True,
                 psTerm=True,
                 aTerm=True,
                 mType="",
                 pa=0.0,
                 dpa=0.0,
                 fieldStr="",
                 spwStr="",
                 phaseCenter="",
                 conjBeams=True,
                 cfBufferSize=512,
                 cfOversampling=20,
                 cfList=None,
                 mode=""):
        self.MSNBuf = MSNBuf
        self.telescopeName = telescopeName
        self.NX = NX
        self.cellSize = cellSize
        self.stokes = stokes
        self.refFreqStr = refFreqStr
        self.nW = nW
        self.cfCacheName = cfCacheName
        self.WBAwp = WBAwp
        self.psTerm = psTerm
        self.aTerm = aTerm
        self.mType = mType
        self.pa = pa
        self.dpa = dpa
        self.fieldStr = fieldStr
        self.spwStr = spwStr
        self.phaseCenter = phaseCenter
        self.conjBeams = conjBeams
        self.cfBufferSize = cfBufferSize
        self.cfOversampling = cfOversampling
        self.cfList = cfList if cfList is not None else []
        self.mode = mode
        self._result = None

    def run(self):
        self._result = coyote2py.coyote(
            MSNBuf=self.MSNBuf,
            telescopeName=self.telescopeName,
            NX=self.NX,
            cellSize=self.cellSize,
            stokes=self.stokes,
            refFreqStr=self.refFreqStr,
            nW=self.nW,
            cfCacheName=self.cfCacheName,
            WBAwp=self.WBAwp,
            psTerm=self.psTerm,
            aTerm=self.aTerm,
            mType=self.mType,
            pa=self.pa,
            dpa=self.dpa,
            fieldStr=self.fieldStr,
            spwStr=self.spwStr,
            phaseCenter=self.phaseCenter,
            conjBeams=self.conjBeams,
            cfBufferSize=self.cfBufferSize,
            cfOversampling=self.cfOversampling,
            cfList=self.cfList,
            mode=self.mode,
        )
        return self

    def __repr__(self):
        return f"Coyote(MSNBuf={self.MSNBuf!r}, telescopeName={self.telescopeName!r}, cfCacheName={self.cfCacheName!r})"
