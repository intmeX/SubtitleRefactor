import translators as ts
from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.tokenfilter import *
from tqdm import tqdm
from typing import List, Set
from ollama import chat
from ollama import ChatResponse
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
            total_sentence += len(file_mark)
        subtitles.mark_words = mark
        print('tokens per sentence:{:.2}'.format(total_token / total_sentence))
        return subtitles


@register_processor
class JpTransProcessor(Processor):
    def __init__(
            self,
            trans_framework: str = 'Ollama',
            trans_model: str = r'hf-mirror.com/SakuraLLM/Sakura-7B-Qwen2.5-v1.0-GGUF',
            retry: int = 3,
            trans_stop: Set = None,
            **kwargs
    ):
        self.trans_framework = trans_framework
        self.trans_model = trans_model
        self.retry = retry
        self.trans_stop = trans_stop
        super(JpTransProcessor, self).__init__(**kwargs)

    def context_translate(self, sentence, key_words_surface):
        single_word = -1
        if len(key_words_surface) == 1:
            single_word = 1
            for word in sentence.split(' '):
                if word == key_words_surface[0]:
                    single_word = 0
                    continue
                else:
                    key_words_surface = key_words_surface.copy()
                    key_words_surface.insert(1 - single_word, word)
                    break
            if len(key_words_surface) == 1:
                single_word = -1
        key_words_length = sum([len(key_word) + 1 for key_word in key_words_surface])
        if self.trans_framework == 'Ollama':
            response: ChatResponse = chat(model=self.trans_model, messages=[
                {
                    "role": "system",
                    # I don't know why does it need double quotations
                    "content": "你是一个动画台词翻译模型，可以流畅通顺地以日本动画台词的风格将日文翻译成简体中文。请在给定的日文\
                    台词““{}””中，联系上下文，正确翻译出用户指定的{}个词语，结果仅包含{}个翻译后的词语，每个词之间用“；”隔开".format(
                        sentence.replace(' ', ''), len(key_words_surface), len(key_words_surface))
                },
                {
                    "role": "user",
                    "content": "；".join(key_words_surface)
                }
            ], options={
                "temperature": 0.1,
                "num_predict": key_words_length * 3,
            })
            if len(response['message']['content']) > key_words_length * 3:
                raise ValueError('output length over {} * 3'.format(key_words_length))
            if single_word == -1:
                return response['message']['content'].split('；')
            else:
                return [response['message']['content'].split('；')[single_word]]
        else:
            return []

    def process(self, subtitles: Subtitle) -> Subtitle:
        if not subtitles.mark_words:
            raise ValueError('No marked keyword found in Subtitles')
        trans = []
        total_token = 0
        total_sentence = 0
        for file_idx in tqdm(range(len(subtitles.files)), desc='Subtitle files', position=0):
            multi_key_words, multisub = subtitles.mark_words[file_idx], subtitles.data[file_idx]
            file_trans = []
            for sentence_idx in tqdm(range(len(multisub)), desc="Sentences", leave=False, position=0):
                key_words, sub = multi_key_words[sentence_idx], multisub[sentence_idx]
                exception_pos = 'file {} sentence "{}"'.format(subtitles.files[file_idx], sub.plaintext)
                base_form_unique = set()
                base_form_check = []
                word_surfaces = []
                for token in key_words:
                    if token['base_form'] not in self.trans_stop and token['base_form'] not in base_form_unique:
                        base_form_unique.add(token['base_form'])
                        word_surfaces.append(token['surface'])
                        base_form_check.append(token['base_form'])
                token_num = len(word_surfaces)
                if not token_num:
                    file_trans.append([])
                    continue
                raw_trans = []
                min_subtract = 999
                for j in range(self.retry):
                    try:
                        raw_trans_cand = self.context_translate(sub.plaintext, word_surfaces)
                        result_num = len(raw_trans_cand)
                        if min_subtract > abs(result_num - token_num):
                            min_subtract = abs(result_num - token_num)
                            raw_trans = raw_trans_cand
                        if not min_subtract:
                            break
                    except Exception as e:
                        print('Exception in request to LLM: {}'.format(exception_pos), e)
                total_token += token_num
                result_num = len(raw_trans)
                if result_num < token_num:
                    raw_trans.extend([''] * (token_num - result_num))
                    print('Unexpected output in {}\nresults: {}, use public api for translation'.format(exception_pos, raw_trans))
                    for token_idx in range(result_num, token_num):
                        try:
                            raw_trans[token_idx] = ts.translate_text(base_form_check[token_idx], from_language='ja', to_language='zh')
                        except Exception as e:
                            print('translator exception in {}'.format(exception_pos))
                elif result_num > token_num:
                    print('Over output num in {}\noutput: {}'.format(exception_pos, raw_trans))
                sentence_trans = [[base_form_check[i], raw_trans[i]] for i in range(len(base_form_check))]
                # print(sentence_trans)
                file_trans.append(sentence_trans)
            trans.append(file_trans)
            total_sentence += len(file_trans)
        subtitles.trans_words = trans
        print('translated tokens per sentence:{:.2}'.format(total_token / total_sentence))
        return subtitles
