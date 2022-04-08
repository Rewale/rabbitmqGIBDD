import inspect
import os
import signal
import sys

from utils.loggers import requests_logger


def get_script_dir(follow_symlinks=True):
    """ Текущая директория скрипта (не зависимо откуда он вызван)"""
    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def get_firefox_addons_dir():
    return get_script_dir()+'/firefox_addons/'


