import os
import pysubs2
from core import Processor
from core import Subtitle


class SubSink(Processor):
    def __init__(
            self,
            root,
            **kwargs,
    ):
        self.root = root
        super(SubSink, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        for file, subtitle in zip(subtitles.files, subtitles.data):
            sub_path = os.path.join(self.root, file)
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
