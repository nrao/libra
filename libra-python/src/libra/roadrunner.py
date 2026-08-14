from . import roadrunner2py


class RoadRunner:
    def __init__(self,
                 vis="",
                 imagename="",
                 modelimagename="",
                 datacolumn="data",
                 sowimageext="",
                 complexgrid="",
                 imsize=None,
                 wprojplanes=1,
                 cell=None,
                 stokes="I",
                 reffreq="3GHz",
                 phasecenter=None,
                 weighting="natural",
                 rmode="norm",
                 robust=0.0,
                 gridder="awphpg",
                 cfcache="",
                 mode="residual",
                 wbawp=True,
                 field="*",
                 spw="*",
                 uvrange="",
                 usepointing=False,
                 normalize=False,
                 pbcor=True,
                 conjbeams=True,
                 pblimit=0.2,
                 pointingoffsetsigdev=None,
                 spwdataiter=True):
        self.vis = vis
        self.imagename = imagename
        self.modelimagename = modelimagename
        self.datacolumn = datacolumn
        self.sowimageext = sowimageext
        self.complexgrid = complexgrid
        self.imsize = imsize if imsize is not None else [4096, 4096]
        self.wprojplanes = wprojplanes
        self.cell = cell if cell is not None else ["0.2arcsec", "0.2arcsec"]
        self.stokes = stokes
        self.reffreq = reffreq
        self.phasecenter = phasecenter if phasecenter is not None else ""
        self.weighting = weighting
        self.rmode = rmode
        self.robust = robust
        self.gridder = gridder
        self.cfcache = cfcache
        self.mode = mode
        self.wbawp = wbawp
        self.field = field
        self.spw = spw
        self.uvrange = uvrange
        self.usepointing = usepointing
        self.normalize = normalize
        self.pbcor = pbcor
        self.conjbeams = conjbeams
        self.pblimit = pblimit
        self.pointingoffsetsigdev = pointingoffsetsigdev if pointingoffsetsigdev is not None else [300.0, 300.0]
        self.spwdataiter = spwdataiter
        self._result = None

    def run(self):
        self._result = roadrunner2py.roadrunner(
            vis=self.vis,
            imagename=self.imagename,
            modelimagename=self.modelimagename,
            datacolumn=self.datacolumn,
            sowimageext=self.sowimageext,
            complexgrid=self.complexgrid,
            imsize=self.imsize,
            wprojplanes=self.wprojplanes,
            cell=self.cell,
            stokes=self.stokes,
            reffreq=self.reffreq,
            phasecenter=self.phasecenter,
            weighting=self.weighting,
            rmode=self.rmode,
            robust=self.robust,
            gridder=self.gridder,
            cfcache=self.cfcache,
            mode=self.mode,
            wbawp=self.wbawp,
            field=self.field,
            spw=self.spw,
            uvrange=self.uvrange,
            usepointing=self.usepointing,
            normalize=self.normalize,
            pbcor=self.pbcor,
            conjbeams=self.conjbeams,
            pblimit=self.pblimit,
            pointingoffsetsigdev=self.pointingoffsetsigdev,
            spwdataiter=self.spwdataiter,
        )
        return self

    def __repr__(self):
        return f"RoadRunner(vis={self.vis!r}, imagename={self.imagename!r}, mode={self.mode!r})"
