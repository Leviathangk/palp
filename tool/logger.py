"""
    修改 loguru 的 logger
"""
import loguru


def debug(*args, sep=' '):
    if len(args) == 1:
        loguru.logger.debug(args[0])
    else:
        loguru.logger.debug(f'{sep}'.join(args))


def info(*args, sep=' '):
    if len(args) == 1:
        loguru.logger.info(args[0])
    else:
        loguru.logger.info(f'{sep}'.join(args))


def warning(*args, sep=' '):
    if len(args) == 1:
        loguru.logger.warning(args[0])
    else:
        loguru.logger.warning(f'{sep}'.join(args))


def error(*args, sep=' '):
    if len(args) == 1:
        loguru.logger.error(args[0])
    else:
        loguru.logger.error(f'{sep}'.join(args))


def exception(arg):
    loguru.logger.exception(arg)
