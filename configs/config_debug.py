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
                'processor': 'JpFuriganaProcessor',
            },
            {
                'processor': 'SubSink',
                'root': r'output/ats_jp_debug',
                'file_retype': 'ass',
                'coordinate': 'original',
            },
        ],
    },
}
