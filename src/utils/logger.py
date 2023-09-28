import logging

from conf import app_name


class Logger:
    def __init__(self, level: int = logging.INFO, name: str = __name__):
        format_string = "{" + '"app_name": "{0}", name: "{1}", "level": "%(levelname)s",' \
                              ' "log_line": "%(filename)s;%(funcName)s;%(lineno)d", "msg": "%(message)s", ' \
                              '"time": "%(asctime)-15s"'.format(app_name, name) + "}"
        logging.basicConfig(level=level,
                            format=format_string,
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(name=name)
