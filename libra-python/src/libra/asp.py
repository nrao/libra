from . import asp2py


class Asp:
    def __init__(self,
                 model=None,
                 psf=None,
                 residual=None,
                 mask=None,
                 size_x=0,
                 size_y=0,
                 psfwidth=0.0,
                 largestscale=-1.0,
                 fusedthreshold=0.0,
                 nterms=1,
                 gain=0.1,
                 threshold=0.0,
                 nsigmathreshold=0.0,
                 nsigma=0.0,
                 cycleniter=-1,
                 cyclefactor=1.0,
                 specmode="mfs",
                 nSubChans=1,
                 chanid=0):
        self.model = model
        self.psf = psf
        self.residual = residual
        self.mask = mask
        self.size_x = size_x
        self.size_y = size_y
        self.psfwidth = psfwidth
        self.largestscale = largestscale
        self.fusedthreshold = fusedthreshold
        self.nterms = nterms
        self.gain = gain
        self.threshold = threshold
        self.nsigmathreshold = nsigmathreshold
        self.nsigma = nsigma
        self.cycleniter = cycleniter
        self.cyclefactor = cyclefactor
        self.specmode = specmode
        self.nSubChans = nSubChans
        self.chanid = chanid
        self._result = None

    def run(self):
        self._result = asp2py.Asp(
            model=self.model,
            psf=self.psf,
            residual=self.residual,
            mask=self.mask,
            size_x=self.size_x,
            size_y=self.size_y,
            psfwidth=self.psfwidth,
            largestscale=self.largestscale,
            fusedthreshold=self.fusedthreshold,
            nterms=self.nterms,
            gain=self.gain,
            threshold=self.threshold,
            nsigmathreshold=self.nsigmathreshold,
            nsigma=self.nsigma,
            cycleniter=self.cycleniter,
            cyclefactor=self.cyclefactor,
            specmode=self.specmode,
            nSubChans=self.nSubChans,
            chanid=self.chanid,
        )
        return self

    def __repr__(self):
        return f"Asp(size_x={self.size_x}, size_y={self.size_y}, specmode={self.specmode!r})"
