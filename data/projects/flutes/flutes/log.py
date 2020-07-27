import functools
import logging
import multiprocessing
import sys
import threading
import time
import traceback
from typing import Callable, List

from termcolor import colored

from .multiproc import get_worker_id
from .types import PathType

__all__ = [
    "get_logging_levels",
    "set_log_file",
    "log",
    "set_logging_level",
    "set_console_logging_function",
]


class MultiprocessingFileHandler(logging.Handler):
    """multiprocessing log handler

    This handler makes it possible for several processes
    to log to the same file by using a queue.

    Credit: https://mattgathu.github.io/multiprocessing-logging-in-python/
    """

    def __init__(self, path: PathType, mode: str = "a"):
        logging.Handler.__init__(self)

        self._handler = logging.FileHandler(path, mode=mode)
        self.queue: 'multiprocessing.Queue[str]' = multiprocessing.Queue(-1)

        thrd = threading.Thread(target=self.receive)
        thrd.daemon = True
        thrd.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            _ = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)


def _remove_handlers(logger):
    while len(logger.handlers) > 0:
        handler = logger.handlers[0]
        handler.close()
        logger.removeHandler(handler)


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
_remove_handlers(LOGGER)  # remove all default handlers

COLOR_MAP = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "white",
}

LOGGING_MAP = {
    "success": LOGGER.info,
    "warning": LOGGER.warning,
    "error": LOGGER.error,
    "info": LOGGER.info,
}
_CONSOLE_LOG_FN: Callable[[str], None] = functools.partial(print, flush=True)

LEVEL_MAP = {
    "success": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "info": logging.INFO,
    "quiet": 999,
}
_CONSOLE_LOGGING_LEVEL = multiprocessing.Value('i', LEVEL_MAP["info"], lock=False)


def get_logging_levels() -> List[str]:
    r"""Return a list of logging levels that the logging system supports."""
    return list(LEVEL_MAP.keys())


def set_log_file(path: PathType, fmt: str = "%(asctime)s %(levelname)s: %(message)s") -> None:
    r"""Set the path of the log file.

    :param path: Path to the log file.
    :param fmt: Logging format.
    """
    _remove_handlers(LOGGER)
    handler = MultiprocessingFileHandler(path, mode="a")
    handler.setFormatter(logging.Formatter(fmt))
    LOGGER.addHandler(handler)


def log(msg: str, level: str = "info", force_console: bool = False, include_proc_id: bool = True) -> None:
    r"""Write a line of log with the specified logging level.

    :param msg: Message to log.
    :param level: Logging level. Available options are ``success``, ``warning``, ``error``, and ``info``.
    :param force_console: If ``True``, will write to console regardless of logging level setting.
    :param include_proc_id: If ``True``, will include the process ID for multiprocessing pool workers.
    """
    if level not in LOGGING_MAP:
        raise ValueError(f"Incorrect logging level '{level}'")
    if include_proc_id:
        worker_id = get_worker_id()
        if worker_id is not None:
            msg = f"(Worker {worker_id:2d}) {msg}"
    if force_console or LEVEL_MAP[level] >= _CONSOLE_LOGGING_LEVEL.value:
        time_str = time.strftime("[%Y-%m-%d %H:%M:%S]")
        _CONSOLE_LOG_FN(colored(time_str, COLOR_MAP[level]) + " " + msg)
    if LOGGER.hasHandlers():
        LOGGING_MAP[level](msg)


def set_logging_level(level: str, console: bool = True, file: bool = True) -> None:
    r"""Set the global logging level to the specified level.

    :param level: Logging level.
    :param console: If ``True``, the specified logging level applies to console output.
    :param file: If ``True``, the specified logging level applies to file output.
    """
    if level not in LEVEL_MAP:
        raise ValueError(f"Incorrect logging level '{level}'")
    if console:
        _CONSOLE_LOGGING_LEVEL.value = LEVEL_MAP[level]
    if file:
        LOGGER.setLevel(LEVEL_MAP[level])


def set_console_logging_function(log_fn: Callable[[str], None]) -> None:
    r"""Set the console logging function **for current process only**."""
    global _CONSOLE_LOG_FN
    _CONSOLE_LOG_FN = log_fn
