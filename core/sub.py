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
        self._mark_words = None
        self._trans_words = None

    @property
    def data(self) -> List[SSAFile]:
        return self._data

    @data.setter
    def data(self, data: List[SSAFile]):
        self._data = data

    @property
    def files(self) -> List[str]:
        return self._files

    @files.setter
    def files(self, files: List[str]):
        self._files = files

    def __str__(self):
        return self.project

    @property
    def mark_words(self) -> List[List[dict]]:
        return self._mark_words

    @mark_words.setter
    def mark_words(self, mark_words: List[List[List[dict]]]):
        self._mark_words = mark_words

    @property
    def trans_words(self) -> List[List[List[List]]]:
        return self._trans_words

    @trans_words.setter
    def trans_words(self, trans_words: List[List[List[List]]]):
        self._trans_words = trans_words


if __name__ == '__main__':
    pass
