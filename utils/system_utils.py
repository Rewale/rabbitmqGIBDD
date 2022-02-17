import inspect
import os
import signal
import sys


def get_script_dir(follow_symlinks=True):
    """ Текущая директория скрипта (не зависимо откуда он вызван)"""
    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


class GracefulKiller:
    """ Перехватывает сигналы завершения работы
    и освобождает память перед выходом"""
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)


    def exit_gracefully(self, *args):
        pass
