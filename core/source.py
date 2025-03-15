import os
import pysubs2
from core.processor import Processor
from core import Subtitle


class SubSource(Processor):
    def __init__(
            self,
            root,
            file_type,
            **kwargs,
    ):
        self.root = root
        self.file_type = file_type
        super(SubSource, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        sub_objs = []
        files = []
        for file in os.listdir(self.root):
            if not file.endswith(self.file_type):
                continue
            sub_objs.append(pysubs2.load(os.path.join(self.root, file), encoding='utf-8'))
            files.append(file)
        subtitles.files = files
        subtitles.data = sub_objs
        return subtitles


if __name__ == '__main__':
    pass
