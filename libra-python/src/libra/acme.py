from . import acme2py


class Acme:
    def __init__(self, imageName="", stats="checkamp"):
        self.imageName = imageName
        self.stats = stats
        self._result = None

    def run(self):
        self._result = acme2py.acme(
            imageName=self.imageName,
            stats=self.stats,
        )
        return self

    def __repr__(self):
        return f"Acme(imageName={self.imageName!r}, stats={self.stats!r})"
