import os
import pysubs2
from typing import List
from core.processor import Processor, register_processor
from core.processor import Subtitle


@register_processor
class SubSource(Processor):
    def __init__(
            self,
            root: str,
            file_type: str = 'ass|srt',
            jp_styles: List = None,
            chs_styles: List = None,
            **kwargs,
    ):
        self.root = root
        self.file_types = file_type.split('|')
        self.styles = dict()
        if jp_styles:
            for style in jp_styles:
                self.styles[style] = 'jp_sentence_bottom'
        if chs_styles:
            for style in chs_styles:
                self.styles[style] = 'chs_top_right'
        super(SubSource, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        sub_objs = []
        files = []
        for file in os.listdir(self.root):
            if not any([file.endswith(suffix) for suffix in self.file_types]):
                continue
            event_file = pysubs2.load(os.path.join(self.root, file), encoding='utf-8')
            for event in event_file:
                if event.style in self.styles:
                    event.style = self.styles[event.style]
            sub_objs.append(event_file)
            file = file[: file.rfind('.')]
            files.append(file)
        subtitles.files = files
        subtitles.data = sub_objs
        return subtitles


@register_processor
class MergeSource(Processor):
    def __init__(
            self,
            root: str,
            file_type: str = 'ass|srt',
            pick_jp_styles: List = None,
            pick_chs_styles: List = None,
            **kwargs,
    ):
        self.root = root
        self.file_types = file_type.split('|')
        self.pick_styles = dict()
        if pick_jp_styles:
            for style in pick_jp_styles:
                self.pick_styles[style] = 'jp_sentence_bottom'
        if pick_chs_styles:
            for style in pick_chs_styles:
                self.pick_styles[style] = 'chs_top_right'
        super(MergeSource, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        file_names = []
        for file_name in os.listdir(self.root):
            if not any([file_name.endswith(suffix) for suffix in self.file_types]):
                continue
            file_names.append(file_name)
        file_num = len(file_names)
        if file_num != len(subtitles.files):
            raise ValueError('Num of Chs subtitles {} cannot match the num of current subtitles {}'.format(file_num, len(subtitles.files)))
        for idx in range(file_num):
            file = file_names[idx]
            origin_file = subtitles.data[idx]
            event_file = pysubs2.load(os.path.join(self.root, file), encoding='utf-8')
            for event in event_file:
                if event.style not in self.pick_styles:
                    continue
                event.style = self.pick_styles[event.style]
                origin_file.append(event)
        return subtitles


if __name__ == '__main__':
    pass
