import time
from typing import List
from pysubs2 import SSAFile


class Subtitle:
    def __init__(
            self,
            project: str = 'untitled',
            language: List[str] = None,
            **kwargs,
    ):
        pro_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.project = pro_time + '_' + project
        self.language = language
        self._data = None
        self._files = None

    @property
    def data(self) -> List[SSAFile]:
        return self._data

    @data.setter
    def data(self, data):
        self._data: List[SSAFile] = data

    @property
    def files(self) -> List[str]:
        return self._files

    @files.setter
    def files(self, files):
        self._files: List[str] = files

    def __str__(self):
        return self.project


if __name__ == '__main__':
    pass
