config = {
    'project': 'untitled',
    'language': ['JP'],
    'processing': {
        'JpFuriganaProcessor': {
            'jp_furigana_server': 'localhost',
            'jp_furigana_port': 15203,
        },
        'processors': [
            {
                'processor': 'SubSource',
                'root': r'C:\apps\cc\[Niconeiko Works] Adachi to Shimamura [1080P_Ma10p_FLAC]\jp_subtitles_debug',
                'file_type': 'ass|srt',
            },
            {
                'processor': 'TextCleaningProcessor',
                'strip_charset': '＜＞ \n',
                'replace_charset': [['\n', ''], ['　', ' ']],
            },
            {
                'processor': 'JpMarkProcessor',
                'keep_filter': ['名詞', '動詞,自立', '動詞,非自立', '形容詞', '副詞', '連体詞'],
                'stop_filter': [
                    '名詞,固有名詞,人名',
                    '名詞,数',
                    '名詞,非自立,助動詞語幹',
                    '副詞,助詞類接続',
                    '名詞,固有名詞,組織',
                    '名詞,代名詞',
                ],
            },
            {
                'processor': 'JpTransProcessor',
                'trans_framework': 'Ollama',
                'trans_model': r'hf-mirror.com/SakuraLLM/Sakura-7B-Qwen2.5-v1.0-GGUF',
                'retry': 3,
                'trans_stop': {'いる', 'ない', 'する', 'こと', 'この', 'その', 'あの', 'とき', '中', '来', 'いい'},
            },
            {
                'processor': 'JpFuriganaProcessor',
            },
            {
                'processor': 'JpKWTransApplyProcessor',
            },
            {
                'processor': 'SubSink',
                'root': r'output/ats_jp_debug',
                'file_retype': 'ass',
            },
        ],
    },
}
