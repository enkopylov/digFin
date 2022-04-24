import xml.etree.ElementTree as et
from datetime import datetime
from typing import NoReturn

import pytest
from lxml import etree

from dig_fin_tz.endpoints import XML_DAILY, XSD_VAL_CURS
from dig_fin_tz.utils import make_get_request, get_currency_code


def test_scheme_matches_xsd(entrypoint: str) -> NoReturn:
    """
    Автотест 'Проверка соответствия тела ответа схеме XSD'

    :param entrypoint: точка входа, на которую делается запрос
    :type: String
    """
    schema_root = etree.parse(XSD_VAL_CURS)
    schema = etree.XMLSchema(schema_root)

    response = make_get_request(entrypoint, XML_DAILY)

    response_body_as_xml = etree.fromstring(response.content)

    assert schema.validate(response_body_as_xml), f'Тело ответа не соответствует схеме. Ошибка: {schema.error_log}'


def test_get_root_tag(entrypoint: str) -> NoReturn:
    """
    Автотест 'Проверка корневого элемента ValCurs в теле ответа'

    :param entrypoint: точка входа, на которую делается запрос
    :type: String
    """
    response = make_get_request(entrypoint, XML_DAILY)

    response_body_as_xml = et.fromstring(response.content)
    xml_tree = et.ElementTree(response_body_as_xml)

    root = xml_tree.getroot()

    assert root.tag == "ValCurs", f'Корневой элемент в теле ответа: {root.tag}'


def test_get_date_in_response(entrypoint: str) -> NoReturn:
    """
    Автотест 'Проверка текущей даты в теле ответа'

    :param entrypoint: точка входа, на которую делается запрос
    :type: String
    """
    response = make_get_request(entrypoint, XML_DAILY)

    response_body_as_xml = et.fromstring(response.content)
    xml_tree = et.ElementTree(response_body_as_xml)

    date_response = xml_tree.getroot().attrib["Date"]
    date_current = datetime.now().date().strftime("%d.%m.%Y")

    assert date_response == date_current, f'Текущая дата: {date_current} не совпадает с датой в ответе {date_response}'


@pytest.mark.parametrize('date_req', ['02/03/2002', '31/12/2010', '15/01/2022'])
def test_get_date_in_response_with_param(entrypoint: str, date_req: str) -> NoReturn:
    """
    Автотест 'Проверка даты в теле ответа, на которую запрашиваются данные'

    :param entrypoint: точка входа, на которую делается запрос
    :type: String

    :param date_req: дата, на которую запрашиваются данные котировок в формате (dd/mm/yyyy)
    :type: String
    """
    param = f'?date_req={date_req}'
    method_with_params = ''.join([XML_DAILY, param])

    response = make_get_request(entrypoint, method_with_params)
    response_body_as_xml = et.fromstring(response.content)
    xml_tree = et.ElementTree(response_body_as_xml)

    date_response = xml_tree.getroot().attrib["Date"]
    date_in_param_formatted = date_req.replace('/', '.')

    assert date_response == date_in_param_formatted, f'Текущая дата: {date_in_param_formatted} не совпадает с датой в ответе {date_response}'


def test_check_type_element_num_code(entrypoint: str) -> NoReturn:
    """
    Автотест 'Проверка значение поля NumCode. Корректности кода валюты'

    :param entrypoint: точка входа, на которую делается запрос
    :type: String
    """
    response = make_get_request(entrypoint, XML_DAILY)

    response_body_as_xml = et.fromstring(response.content)
    xml_tree = et.ElementTree(response_body_as_xml)
    root = xml_tree.getroot()

    list_currency_code = get_currency_code(entrypoint)

    for value in root:
        for num_code in value.iter('NumCode'):
            assert num_code.text.isdigit() is True, f'Поле NumCode содержит не только цифры. NumCode в ответе: {num_code.text}'
            assert int(
                num_code.text) in list_currency_code, f'Код валюты {num_code.text} из ответа не найден в "Cправочник по кодам валют"'


def test_presence_of_fields_in_the_response(entrypoint: str) -> NoReturn:
    """
    Автотест 'Проверка заполненности полей ответа'

    :param entrypoint: точка входа, на которую делается запрос
    :type: String
    """
    response = make_get_request(entrypoint, XML_DAILY)

    response_body_as_xml = et.fromstring(response.content)
    xml_tree = et.ElementTree(response_body_as_xml)

    root = xml_tree.getroot()

    for valute in root:
        for num_code in valute:
            assert num_code.text, f'В элементе {valute.attrib["ID"]} встретилось пустое поле {num_code.tag}'
