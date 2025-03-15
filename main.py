import importlib
import argparse


def get_config():
    config_parser = argparse.ArgumentParser()
    config_parser.add_argument('--config', type=str, default='', required=True)
    args, _ = config_parser.parse_known_args()
    spec = importlib.util.spec_from_file_location('config', args.config)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config.config


def main():
    # config_dict = get_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='debug', choices=['default', 'debug'])
    parser.add_argument('--sink.root', type=str, default='debug')
    args = parser.parse_args()
    print(args.__getattribute__('sink.root'))
    print(vars(args))


if __name__ == '__main__':
    main()
