import pytest
import urllib3


@pytest.fixture(scope='session', autouse=True)
def disable_request_warnings():
    """
    Отключает варнинги со стороны urllib3 для работы requests по протоколу https.
    Почитать тут: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
