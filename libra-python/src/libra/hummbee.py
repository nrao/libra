from . import hummbee2py


class Hummbee:
    def __init__(self,
                 imagename="",
                 modelimagename="",
                 deconvolver="hogbom",
                 scales=None,
                 largestscale=-1,
                 fusedthreshold=0.0,
                 nterms=1,
                 gain=0.1,
                 threshold=0.0,
                 nsigma=0.0,
                 cycleniter=-1,
                 cyclefactor=1.0,
                 mask="",
                 specmode="mfs",
                 pbcor=False,
                 mode="deconvolve"):
        self.imagename = imagename
        self.modelimagename = modelimagename
        self.deconvolver = deconvolver
        self.scales = scales if scales is not None else []
        self.largestscale = largestscale
        self.fusedthreshold = fusedthreshold
        self.nterms = nterms
        self.gain = gain
        self.threshold = threshold
        self.nsigma = nsigma
        self.cycleniter = cycleniter
        self.cyclefactor = cyclefactor
        self.mask = mask
        self.specmode = specmode
        self.pbcor = pbcor
        self.mode = mode
        self._result = None

    def run(self):
        self._result = hummbee2py.hummbee(
            imagename=self.imagename,
            modelimagename=self.modelimagename,
            deconvolver=self.deconvolver,
            scales=self.scales,
            largestscale=self.largestscale,
            fusedthreshold=self.fusedthreshold,
            nterms=self.nterms,
            gain=self.gain,
            threshold=self.threshold,
            nsigma=self.nsigma,
            cycleniter=self.cycleniter,
            cyclefactor=self.cyclefactor,
            mask=self.mask,
            specmode=self.specmode,
            pbcor=self.pbcor,
            mode=self.mode,
        )
        return self

    def __repr__(self):
        return f"Hummbee(imagename={self.imagename!r}, deconvolver={self.deconvolver!r}, mode={self.mode!r})"
