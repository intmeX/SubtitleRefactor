from core.sub import Subtitle
from core.source import SubSource
from core.sink import SubSink
from core.processor import register_processor, PROCESSOR, Compose
from core.processor import Processor, JpFuriganaProcessor
from core.analysis_processor import JpTransProcessor, JpMarkProcessor
from core.format_processor import TextCleaningProcessor, JpKWTransApplyProcessor


__all__ = [
    'Subtitle',
    'Processor',
    'SubSource',
    'SubSink',
    'Compose',
    'register_processor',
    'get_processor',
    'JpFuriganaProcessor',
    'TextCleaningProcessor',
    'JpTransProcessor',
    'JpMarkProcessor',
    'JpKWTransApplyProcessor',
]


def get_processor(cls_cfgs, obj_cfg):
    cls_name = obj_cfg.get('processor', None)
    if not cls_name:
        raise ValueError('No processor name')
    cls = PROCESSOR.get(cls_name, None)
    if cls:
        cls_cfg = cls_cfgs.get(cls_name, dict())
        return cls(**obj_cfg, **cls_cfg)
    else:
        raise ModuleNotFoundError('{} processor not found'.format(cls_name))
