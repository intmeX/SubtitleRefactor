import os
import pysubs2
from core.processor import Processor, register_processor
from core.processor import Subtitle


@register_processor
class SubSource(Processor):
    def __init__(
            self,
            root: str,
            file_type: str,
            **kwargs,
    ):
        self.root = root
        self.file_types = file_type.split('|')
        super(SubSource, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        sub_objs = []
        files = []
        for file in os.listdir(self.root):
            if not any([file.endswith(suffix) for suffix in self.file_types]):
                continue
            sub_objs.append(pysubs2.load(os.path.join(self.root, file), encoding='utf-8'))
            file = file[: file.rfind('.')]
            files.append(file)
        subtitles.files = files
        subtitles.data = sub_objs
        return subtitles


if __name__ == '__main__':
    pass
