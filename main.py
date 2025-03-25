import importlib
import argparse
from core import Subtitle, Compose, get_processor


def get_config():
    # get the config file
    config_parser = argparse.ArgumentParser()
    config_parser.add_argument('--config', type=str, default='', required=True)
    args, _ = config_parser.parse_known_args()
    spec = importlib.util.spec_from_file_location('config', args.config)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    config_dict = config.config
    print('Successfully load config file')
    # use command line args cover the config dict
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='default', choices=['default', 'debug'])
    args, _ = parser.parse_known_args()
    args = vars(args)
    for key, value in args.items():
        key_list = key.split('.')
        pt = config_dict
        for idx in range(len(key_list) - 1):
            pt.setdefault(key_list[idx], dict())
            pt = pt[key_list[idx]]
        pt[key_list[-1]] = value
    return config_dict


def main():
    cfg = get_config()
    subtitles = Subtitle(**cfg)
    processing_cfg = cfg.get('processing', dict)
    processors = processing_cfg.pop('processors', [])
    solutions = Compose([get_processor(processing_cfg, processor_cfg) for processor_cfg in processors])
    results = solutions(subtitles)
    print('{}: Subtitles processing completed'.format(results))


if __name__ == '__main__':
    main()
