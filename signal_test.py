from utils.system_utils import get_script_dir


def test_get_dir():
    assert get_script_dir() == "~/Рабочий стол/parsers/parser-gibdd-docker/rabbitMQ"
