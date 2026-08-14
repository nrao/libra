from . import dale2py


class Dale:
    def __init__(self,
                 imageName="",
                 wtimageName="",
                 sowimageName="",
                 normtype="flatnoise",
                 imType="psf",
                 pblimit=0.2):
        self.imageName = imageName
        self.wtimageName = wtimageName
        self.sowimageName = sowimageName
        self.normtype = normtype
        self.imType = imType
        self.pblimit = pblimit
        self._result = None

    def run(self):
        self._result = dale2py.dale(
            imageName=self.imageName,
            wtimageName=self.wtimageName,
            sowimageName=self.sowimageName,
            normtype=self.normtype,
            imType=self.imType,
            pblimit=self.pblimit,
        )
        return self

    def __repr__(self):
        return f"Dale(imageName={self.imageName!r}, normtype={self.normtype!r}, imType={self.imType!r})"
