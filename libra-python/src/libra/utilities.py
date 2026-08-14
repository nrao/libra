from . import utilities2py


class GetChunk:
    def __init__(self, imageName="", type=""):
        self.imageName = imageName
        self.type = type
        self._result = None

    def run(self):
        self._result = utilities2py.getchunk(
            imageName=self.imageName,
            type=self.type,
        )
        return self

    @property
    def result(self):
        return self._result

    def __repr__(self):
        return f"GetChunk(imageName={self.imageName!r}, type={self.type!r})"
