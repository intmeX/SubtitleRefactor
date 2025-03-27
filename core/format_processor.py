from copy import deepcopy
from tqdm import tqdm
from typing import List
from pysubs2 import SSAStyle, Alignment, Color
from core.sub import Subtitle
from core.processor import Processor, register_processor


@register_processor
class KWTransApplyProcessor(Processor):
    def __init__(
            self,
            **kwargs,
    ):
        super(KWTransApplyProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        if not subtitles.trans_words:
            raise ValueError('No translated keyword found in Subtitles')
        for file_idx in tqdm(range(len(subtitles.files)), desc='Subtitle files', position=0):
            multi_trans_words, multisub = subtitles.trans_words[file_idx], subtitles.data[file_idx]
            for sentence_idx in tqdm(range(len(multisub)), desc="Sentences", leave=False, position=0):
                trans_key_words, sub = multi_trans_words[sentence_idx], multisub[sentence_idx]
                if not trans_key_words:
                    continue
                anno_sub = deepcopy(sub)
                anno_sub.plaintext = '\n'.join([':'.join(key_trans) for key_trans in trans_key_words])
                anno_sub.style = 'jp_keywords_left'
                multisub.append(anno_sub)
        return subtitles


@register_processor
class KWStyleProcessor(Processor):
    def __init__(
            self,
            fontname: str = 'UD Digi Kyokasho N-B',
            sentence_size: int = 20,
            keyword_size: int = 12,
            trans_chs_size: int = 8,
            outline_size: float = 1.0,
            sentence_offset_ms: int = 0,
            keyword_offset_ms: int = 0,
            trans_chs_offset_ms: int = 0,
            **kwargs,
    ):
        self.fontname = fontname
        self.sentence_size = sentence_size
        self.keyword_size = keyword_size
        self.trans_chs_size = trans_chs_size
        self.outline_size = outline_size
        self.offset_ms = {
            'jp_sentence_bottom': sentence_offset_ms,
            'jp_keywords_left': keyword_offset_ms,
            'chs_top_right': trans_chs_offset_ms,
        }
        super(KWStyleProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for file_idx in tqdm(range(len(subtitles.files)), desc='Subtitle files', position=0):
            multisub = subtitles.data[file_idx]
            multisub.styles.update({
                'jp_sentence_bottom': SSAStyle(
                    fontname=self.fontname,
                    fontsize=self.sentence_size,
                    alignment=Alignment.BOTTOM_CENTER,
                    primarycolor=Color(240, 156, 240),
                    outlinecolor=Color(0, 0, 0, 64),
                    backcolor=Color(0, 0, 0, 255),
                    outline=self.outline_size,
                ),
                'jp_keywords_left': SSAStyle(
                    fontname=self.fontname,
                    fontsize=self.keyword_size,
                    alignment=Alignment.MIDDLE_LEFT,
                    primarycolor=Color(64, 148, 230, 224),
                    outlinecolor=Color(0, 0, 0, 64),
                    backcolor=Color(0, 0, 0, 255),
                    outline=self.outline_size,
                ),
                'chs_top_right': SSAStyle(
                    fontname=self.fontname,
                    fontsize=self.trans_chs_size,
                    alignment=Alignment.TOP_RIGHT,
                    primarycolor=Color(64, 148, 230, 224),
                    outlinecolor=Color(0, 0, 0, 224),
                    backcolor=Color(0, 0, 0, 255),
                    outline=self.outline_size,
                ),
            })
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                if sub.style not in self.offset_ms:
                    continue
                    # raise KeyError('Undefined style in subtitles')
                offset_ms = self.offset_ms[sub.style]
                sub.start += offset_ms
                sub.end += offset_ms
        return subtitles


@register_processor
class Ruby2KrokProcessor(Processor):
    def __init__(
            self,
            convert_part: List,
            **kwargs
    ):
        self.convert_part = convert_part
        self.sep = r'{\k1}'
        self.replace_pair = [[r'<ruby>', self.sep], [r'</ruby>', self.sep], [r'<rp>(</rp>', r'|'], [r'<rp>)</rp>', r''], [r'<rt>', ''], [r'</rt>', '']]
        super(Ruby2KrokProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for multisub in tqdm(subtitles.data, desc='Subtitle files', position=0):
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                if sub.style not in self.convert_part:
                    continue
                for src_str, des_str in self.replace_pair:
                    tmp_str = sub.text
                    tmp_str = tmp_str.replace(src_str, des_str)
                    sub.text = tmp_str
                if not sub.text.startswith(self.sep):
                    sub.text = self.sep + sub.text
        return subtitles


@register_processor
class Ruby2BaseProcessor(Processor):
    def __init__(
            self,
            convert_part: List,
            **kwargs
    ):
        self.convert_part = convert_part
        self.replace_pair = [
            [r'<ruby>', r'<ruby-container><ruby-base>'],
            [r'</ruby>', r'</ruby-container>'],
            [r'<rp>(</rp>', r'</ruby-base>'],
            [r'<rp>)</rp>', ''],
            [r'<rt>', r'<ruby-text>'],
            [r'</rt>', r'</ruby-text>'],
        ]
        super(Ruby2BaseProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for multisub in tqdm(subtitles.data, desc='Subtitle files', position=0):
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                if sub.style not in self.convert_part:
                    continue
                for src_str, des_str in self.replace_pair:
                    sub.text = sub.text.replace(src_str, des_str)
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
        self.apply_styles = ['jp_sentence_bottom']
        super(TextCleaningProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for multisub in tqdm(subtitles.data, desc='Subtitle files', position=0):
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                if sub.style not in self.apply_styles:
                    continue
                sub.plaintext = sub.plaintext.strip(self.strip_charset)
                for src_str, des_str in self.replace_charset:
                    sub.plaintext = sub.plaintext.replace(src_str, des_str)
        return subtitles
