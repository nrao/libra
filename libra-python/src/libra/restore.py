from . import restore2py


class Restore:
    def __init__(self,
                 model=None,
                 residual=None,
                 image=None,
                 size_x=0,
                 size_y=0,
                 refi=0.0,
                 refj=0.0,
                 inci=0.0,
                 incj=0.0,
                 majaxis=0.0,
                 minaxis=0.0,
                 pa=0.0,
                 pbcor=False,
                 pb=None,
                 image_pbcor=None):
        self.model = model
        self.residual = residual
        self.image = image
        self.size_x = size_x
        self.size_y = size_y
        self.refi = refi
        self.refj = refj
        self.inci = inci
        self.incj = incj
        self.majaxis = majaxis
        self.minaxis = minaxis
        self.pa = pa
        self.pbcor = pbcor
        self.pb = pb
        self.image_pbcor = image_pbcor
        self._result = None

    def run(self):
        self._result = restore2py.restore(
            model=self.model,
            residual=self.residual,
            image=self.image,
            size_x=self.size_x,
            size_y=self.size_y,
            refi=self.refi,
            refj=self.refj,
            inci=self.inci,
            incj=self.incj,
            majaxis=self.majaxis,
            minaxis=self.minaxis,
            pa=self.pa,
            pbcor=self.pbcor,
            pb=self.pb,
            image_pbcor=self.image_pbcor,
        )
        return self

    def __repr__(self):
        return f"Restore(size_x={self.size_x}, size_y={self.size_y}, pbcor={self.pbcor})"
