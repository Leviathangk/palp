"""
    修改 loguru 的 logger

    推荐还是使用 loguru 的logger，这里只是免于拼接，但是不能输出日志的位置
"""
import loguru


def debug(*args, sep=' '):
    args = [str(i) for i in args]

    if len(args) == 1:
        loguru.logger.debug(args[0])
    else:
        loguru.logger.debug(f'{sep}'.join(args))


def info(*args, sep=' '):
    args = [str(i) for i in args]

    if len(args) == 1:
        loguru.logger.info(args[0])
    else:
        loguru.logger.info(f'{sep}'.join(args))


def warning(*args, sep=' '):
    args = [str(i) for i in args]

    if len(args) == 1:
        loguru.logger.warning(args[0])
    else:
        loguru.logger.warning(f'{sep}'.join(args))


def error(*args, sep=' '):
    args = [str(i) for i in args]

    if len(args) == 1:
        loguru.logger.error(args[0])
    else:
        loguru.logger.error(f'{sep}'.join(args))


def exception(arg):
    loguru.logger.exception(arg)
