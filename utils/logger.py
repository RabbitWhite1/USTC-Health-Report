import logging
import os
import platform
import os.path as osp
import yaml


class Logger:
    loggers = {}
    level = None
    fmt = None
    filename = None

    @staticmethod
    def get_logger(log_type='reporter'):
        if log_type not in Logger.loggers:
            with open(osp.join(osp.dirname(__file__), '..', 'etc', 'logger.yaml'), 'r') as f:
                config = yaml.load(f.read(), Loader=yaml.BaseLoader)[log_type]
                level_map = {'debug': logging.DEBUG,
                             'info': logging.INFO,
                             'warn': logging.WARN,
                             'warning': logging.WARN,
                             'error': logging.ERROR,
                             'fatal': logging.FATAL,
                             'critical': logging.CRITICAL}

                level = level_map[config['level'].lower()]
                filename = osp.realpath(osp.join(osp.dirname(__file__), '..', 'etc', *osp.split(config['filename'])))
                if not osp.exists(osp.dirname(filename)):
                    os.makedirs(osp.dirname(filename))
                logger = Logger.init_logger(level=level, fmt=config['fmt'], filename=filename)
                Logger.loggers[log_type] = logger
        return Logger.loggers[log_type]

    @staticmethod
    def init_logger(level=logging.INFO,
                    fmt='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
                    filename: str = None):
        logger = logging.getLogger(filename)
        logger.setLevel(level)

        fmt = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')

        # stream handler
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

        if filename:
            # file handler
            fh = logging.FileHandler(filename, encoding='utf-8')
            fh.setLevel(level)
            fh.setFormatter(fmt)
            logger.addHandler(fh)

        logger.setLevel(level)
        return logger


if platform.platform().find('Windows-10') != -1:
    win10 = True
    try:
        from win10toast import ToastNotifier
    except ModuleNotFoundError as e:
        print('please install win10toast for convenience: pip install win10toast')
        win10 = False

if win10:
    def toast(message):
        if platform.platform().find('Windows-10') != -1:
            toaster = ToastNotifier()
            toaster.show_toast('中国科大健康打卡',
                            message,
                            icon_path=None,
                            duration=5,
                            threaded=True)
else:
    def toast(message):
        pass
