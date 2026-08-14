from . import tableinfo2py


class TableInfo:
    def __init__(self, MSNBuf="", OutBuf="", verbose=False):
        self.MSNBuf = MSNBuf
        self.OutBuf = OutBuf
        self.verbose = verbose
        self._result = None

    def run(self):
        self._result = tableinfo2py.tableinfo(
            MSNBuf=self.MSNBuf,
            OutBuf=self.OutBuf,
            verbose=self.verbose,
        )
        return self

    def __repr__(self):
        return f"TableInfo(MSNBuf={self.MSNBuf!r}, verbose={self.verbose})"
