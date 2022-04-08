from utils.system_utils import get_script_dir, get_firefox_addons_dir


def test_get_addons_dir():
    path = get_firefox_addons_dir()
    assert path == "/home/kolchanovaa/Рабочий стол/parsers/parsers_gibdd_rabbitMQ/utils/firefox_addons"
