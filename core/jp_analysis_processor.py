from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.tokenfilter import *
from tqdm import tqdm
from typing import List
from core.sub import Subtitle
from core.processor import Processor, register_processor


@register_processor
class JpMarkProcessor(Processor):
    def __init__(
            self,
            keep_filter: List[str] = None,
            stop_filter: List[str] = None,
            **kwargs
    ):
        self.keep_filter = keep_filter
        self.stop_filter = stop_filter
        self.tokenizer = Tokenizer()
        self.token_filters = [
            CompoundNounFilter(),
            POSKeepFilter(self.keep_filter),
            POSStopFilter(self.stop_filter),
            LowerCaseFilter()
        ]
        self.plain_token_filters = [
            CompoundNounFilter(),
            LowerCaseFilter()
        ]
        self.analyzer = Analyzer(tokenizer=self.tokenizer, token_filters=self.token_filters)
        self.plain_analyzer = Analyzer(tokenizer=self.tokenizer, token_filters=self.plain_token_filters)
        super(JpMarkProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        mark = []
        total_token = 0
        total_sentence = 0
        for multisub in tqdm(subtitles.data, desc='Subtitle files', position=0):
            file_mark = []
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                sentence_mark = []
                for token in self.analyzer.analyze(sub.plaintext):
                    if token.extra and any([stop_str in token.extra[0] for stop_str in self.stop_filter]):
                        continue
                    word_mark = {
                        'surface': token.surface,
                        'base_form': token.base_form,
                        'extra0': token.extra[0] if token.extra else token.part_of_speech,
                    }
                    if token.extra and token.part_of_speech != token.extra[0]:
                        word_mark['extra0'] += ',' + token.part_of_speech
                    sentence_mark.append(word_mark)
                    # print(word_mark)
                    total_token += 1
                file_mark.append(sentence_mark)
                new_plaintext = ''
                pre_token = ''
                for token in self.plain_analyzer.analyze(sub.plaintext):
                    if pre_token and not ('記号' in pre_token or '記号' in token.part_of_speech):
                        sep = ' '
                    else:
                        sep = ''
                    new_plaintext = new_plaintext + sep + token.surface
                    pre_token = token.part_of_speech
                sub.plaintext = new_plaintext
            mark.append(file_mark)
            total_sentence += len(multisub)
        subtitles.mark_plaintext = mark
        print('tokens per sentence:{:.2}'.format(total_token / total_sentence))
        return subtitles
