import pysubs2
import execjs
from core import Subtitle


class Processor:
    def __init__(
            self,
            coordinate='original',
            **kwargs,
    ):
        self.coordinate = coordinate

    def __call__(self, **kwargs):
        return self.process(**kwargs)

    def process(self, **kwargs):
        raise NotImplementedError


class JpFuriganaProcessor(Processor):
    def __init__(self, **kwargs):
        super(JpFuriganaProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for multiline_sub in subtitles.data:
            for sub in multiline_sub:
                print(sub)
        return subtitles


if __name__ == '__main__':
    pass
