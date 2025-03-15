import os
import time
from typing import List
from pysubs2 import SSAFile


class Subtitle:
    def __init__(
            self,
            project='untitled',
            language=None,
            **kwargs,
    ):
        pro_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.project = pro_time + '_' + project
        self.language = language

    @property
    def data(self) -> List[SSAFile]:
        return self.data

    @data.setter
    def data(self, data):
        self.data: List[SSAFile] = data

    @property
    def files(self) -> List[str]:
        return self.files

    @files.setter
    def files(self, files):
        self.files: List[str] = files


if __name__ == '__main__':
    pass
