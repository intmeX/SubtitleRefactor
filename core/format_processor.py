from copy import deepcopy
from tqdm import tqdm
from typing import List
from pysubs2 import SSAStyle, Alignment, Color
from core.sub import Subtitle
from core.processor import Processor, register_processor


@register_processor
class JpKWTransApplyProcessor(Processor):
    def __init__(
            self,
            **kwargs
    ):
        super(JpKWTransApplyProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        if not subtitles.trans_words:
            raise ValueError('No translated keyword found in Subtitles')
        for file_idx in tqdm(range(len(subtitles.files)), desc='Subtitle files', position=0):
            multi_trans_words, multisub = subtitles.trans_words[file_idx], subtitles.data[file_idx]
            multisub.styles.update({
                "bottom": SSAStyle(fontname='UD Digi Kyokasho N-B', fontsize=20, alignment=Alignment.BOTTOM_CENTER, primarycolor=Color(240, 156, 240)),
                "left": SSAStyle(fontname='UD Digi Kyokasho N-B', fontsize=18, alignment=Alignment.MIDDLE_LEFT, primarycolor=Color(64, 148, 230, 128)),
            })
            for sentence_idx in tqdm(range(len(multisub)), desc="Sentences", leave=False, position=0):
                trans_key_words, sub = multi_trans_words[sentence_idx], multisub[sentence_idx]
                sub.style = 'bottom'
                anno_sub = deepcopy(sub)
                anno_sub.plaintext = '\n'.join([':'.join(key_trans) for key_trans in trans_key_words])
                anno_sub.style = 'left'
                multisub.append(anno_sub)
        return subtitles


@register_processor
class TextCleaningProcessor(Processor):
    def __init__(
            self,
            strip_charset: str,
            replace_charset: List,
            **kwargs
    ):
        self.strip_charset = strip_charset
        self.replace_charset = replace_charset
        super(TextCleaningProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for multisub in tqdm(subtitles.data, desc='Subtitle files', position=0):
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                sub.plaintext = sub.plaintext.strip(self.strip_charset)
                for src_str, des_str in self.replace_charset:
                    sub.plaintext = sub.plaintext.replace(src_str, des_str)
        return subtitles
