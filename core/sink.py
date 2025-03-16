import os
import pysubs2
from core.processor import Processor, register_processor
from core.sub import Subtitle


@register_processor
class SubSink(Processor):
    def __init__(
            self,
            root: str,
            file_retype: str,
            **kwargs,
    ):
        self.root = root
        self.file_retype = file_retype
        super(SubSink, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        for file, subtitle in zip(subtitles.files, subtitles.data):
            sub_path = os.path.join(self.root, file + '.' + self.file_retype)
            try:
                subtitle.save(sub_path, encoding='utf-8')
            except Exception as e:
                print('Error in saving {}'.format(sub_path), e)
                continue
            else:
                print('{} was Successfully saved'.format(sub_path))
        return subtitles


if __name__ == '__main__':
    pass
