import xml.etree.ElementTree as et
from typing import Optional, Dict, Union, List

import pytest
import requests
from requests import Response
from requests.exceptions import ReadTimeout

from dig_fin_tz.endpoints import XML_VAL


def make_get_request(
        entrypoint: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Union[str, List[str]]]] = None
) -> Response:
    """
    Посылает GET запрос на сервер.
    Возвращает ответ сервера.
    Выставлен таймаут запроса 10 секунд.

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param method: тестируемый API-метод
    :type: String

    :param headers: хэдерсы запроса
    :type: Dictionary

    :param params: опциональный параметр get-запроса
    :type: Dictionary

    :return: возвращает объект Response - ответ сервера.
    :rtype: Response
    """
    try:
        response = requests.get(
            f'{entrypoint}{method}',
            params=params,
            headers=headers,
            verify=False,
            timeout=10,
        )
    except ReadTimeout:
        pytest.fail('Время установки соединения превышает предельно допустимое значение')

    return response


def get_list_of_elements(root_param: et.Element, value: str) -> List:
    """
    Получение списка значений заданного элемента

    :param root_param: Корневой элемент дерева структуры xml
    :type: xml.etree.ElementTree.Element

    :param value: Значение поля, для которого требуется собрать список
    :type: String

    :return: возвращает список значений для заданного элемента
    :rtype: List
    """
    elements_list = []

    for cod_val in root_param:
        for parent_code in cod_val.iter(value):
            if parent_code.text:
                parent_code.text = int(parent_code.text)
                elements_list.append(parent_code.text)

    return elements_list


def get_currency_code(entrypoint: str) -> List:
    """
    Получение кодов валют из справочника

    :param entrypoint: точка входа, на которую делается запрос
    :type: String

    :return: возвращает список значений кодов валют из 'Справочник кодов валют'
    :rtype: List
    """
    param_d_everyday = '?d=0'  # Коды валют устанавливаемые ежедневно
    param_d_monthly = '?d=1'  # Коды валют устанавливаемые ежемесячно.

    method_with_param_d_everyday = ''.join([XML_VAL, param_d_everyday])
    method_with_param_d_monthly = ''.join([XML_VAL, param_d_monthly])

    response_param_d_everyday = make_get_request(entrypoint, method_with_param_d_everyday)

    response_param_d_everyday_body_as_xml = et.fromstring(response_param_d_everyday.content)
    xml_tree = et.ElementTree(response_param_d_everyday_body_as_xml)
    root_param_d_everyday = xml_tree.getroot()

    response_param_d_monthly = make_get_request(entrypoint, method_with_param_d_monthly)

    response_param_d_monthly_body_as_xml = et.fromstring(response_param_d_monthly.content)
    xml_tree = et.ElementTree(response_param_d_monthly_body_as_xml)
    root_param_d_monthly = xml_tree.getroot()

    currency_list_param_d_everyday = get_list_of_elements(root_param_d_everyday, 'ISO_Num_Code')
    currency_list_param_d_monthly = get_list_of_elements(root_param_d_monthly, 'ISO_Num_Code')

    currency_list = currency_list_param_d_everyday + currency_list_param_d_monthly
    currency_list = list(set(currency_list))

    return currency_list
