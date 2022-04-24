import pytest
import urllib3

from dig_fin_tz.settings import URL


@pytest.fixture(scope='session', autouse=True)
def disable_request_warnings():
    """
    Отключает варнинги со стороны urllib3 для работы requests по протоколу https.
    Почитать тут: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope='session')
def entrypoint() -> str:
    """
    Фикстура получения точки входа для апи-запросов.

    :return: возвращает entrypoint для апи-запросов.
    :rtype: String
    """
    return URL
