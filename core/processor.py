import time
import requests
import subprocess
from typing import List
from tqdm import tqdm
from core.sub import Subtitle


PROCESSOR = dict()


def register_processor(cls):
    PROCESSOR[cls.__name__] = cls
    return cls


@register_processor
class Processor:
    def __init__(
            self,
            **kwargs,
    ):
        pass

    def __call__(self, subtitles: Subtitle) -> Subtitle:
        print('{} starting...'.format(self.__class__.__name__))
        return self.process(subtitles)

    def process(self, subtitles: Subtitle) -> Subtitle:
        raise NotImplementedError


@register_processor
class JpFuriganaProcessor(Processor):
    furigana_server: str = 'localhost'
    furigana_port: int = 15203
    furigana_url: str = 'http://' + furigana_server + ':' + str(furigana_port) + '/furigana/'
    furigana_running: bool = False
    process_count: int = 0

    @classmethod
    def init_furigana(
            cls,
            furigana_server: str = 'localhost',
            furigana_port: int = 15203,
            **kwargs,
    ):
        cls.furigana_server = furigana_server
        cls.furigana_port = furigana_port
        cls.furigana_url = 'http://' + cls.furigana_server + ':' + str(cls.furigana_port) + '/furigana/'
        cls.close_furigana()
        cls.start_furigana()

    @classmethod
    def close_furigana(cls):
        try:
            res = requests.get(cls.furigana_url + 'exit')
            print('Closing furigana server:', res.text)
        except Exception as e:
            # print('Closing furigana server:', e)
            pass
        cls.furigana_running = False

    @classmethod
    def start_furigana(cls):
        if cls.furigana_running:
            return
        cls.server_process = subprocess.Popen([
            'node',
            'scripts/furigana.mjs',
            str(cls.furigana_port),
        ])
        time.sleep(2.0)
        if not cls.server_process.returncode:
            print('Furigana server started')
        else:
            print('Furingana error with return code {}'.format(cls.server_process.returncode))
            raise Exception('Error in furigana start')
        cls.furigana_running = True

    @classmethod
    def get_furigana(cls, sentence: str, mode_str: str, to_str: str):
        try:
            json_dict = {
                'sentence': sentence,
                'mode_str': mode_str,
                'to_str': to_str,
            }
            furigana = requests.post(cls.furigana_url, data=json_dict).text
        except Exception as e:
            print('Error in furigana requesting')
            raise e
        return furigana

    def __init__(self, **kwargs):
        if not JpFuriganaProcessor.process_count:
            JpFuriganaProcessor.init_furigana(**kwargs)
        JpFuriganaProcessor.process_count += 1
        self.apply_styles = ['jp_sentence_bottom']
        super(JpFuriganaProcessor, self).__init__(**kwargs)

    def process(self, subtitles: Subtitle) -> Subtitle:
        for i in tqdm(range(len(subtitles.data)), desc='Subtitle files', position=0):
            multisub = subtitles.data[i]
            for sub in tqdm(multisub, desc="Sentences", leave=False, position=0):
                if sub.style not in self.apply_styles:
                    continue
                try:
                    furigana = JpFuriganaProcessor.get_furigana(sub.plaintext, 'furigana', 'hiragana')
                    sub.plaintext = furigana
                except Exception as e:
                    print('Error in furigana for file: {}  line: {}  sentence: {}'.format(
                        subtitles.files[i],
                        i,
                        sub.plaintext,
                    ))
                    raise e
            # print('Completed {} sentences\' furigana for {}'.format(len(multiline_sub), subtitles.files[i]))
        return subtitles

    def __del__(self):
        JpFuriganaProcessor.process_count -= 1
        if not JpFuriganaProcessor.process_count:
            JpFuriganaProcessor.close_furigana()


class Compose:
    def __init__(
            self,
            process_list: List[Processor],
    ):
        self.functions = process_list

    def __call__(self, subtitles: Subtitle) -> Subtitle:
        for func in self.functions:
            start_time = time.time()
            subtitles = func(subtitles)
            print('{} Completed in {}s'.format(func.__class__.__name__, time.time() - start_time))
        return subtitles


if __name__ == '__main__':
    pass
