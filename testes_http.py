from typing import Literal, TypeAlias, get_args

import httpx
import respx

URL_COTACAO = 'https://economia.awesomeapi.com.br/json/last/{}'
Moeda: TypeAlias = Literal['EUR', 'USD', 'BTC']


def cotacao(moeda: Moeda):
    code = f'{moeda}-BRL'
    try:
        response = httpx.get(URL_COTACAO.format(code))
        data = response.json()[code.replace('-', '')]

        return f'Última cotação: {data["high"]}'

    except KeyError:
        return f'Código de moeda inválido. Use {get_args(Moeda)}'

    except httpx.InvalidURL:
        return f'Código de moeda inválido. Use {get_args(Moeda)}'

    except httpx.ConnectError:
        return 'Erro de conexão, tente mais tarde.'

    except httpx.TimeoutException:
        return 'Erro de conexão, tente mais tarde.'


@respx.mock
def test_dolar():
    # Arange
    mocked_response = httpx.Response(200, json={'USDBRL': {'high': 5.7945}})
    respx.get(URL_COTACAO.format('USD-BRL')).mock(mocked_response)

    # Act
    result = cotacao('USD')

    # Assert
    assert result == 'Última cotação: 5.7945'


@respx.mock
def test_moeda_errada():
    mocked_response = httpx.Response(200, json={})

    respx.get(URL_COTACAO.format('MDT-BRL')).mock(mocked_response)

    result = cotacao('MDT')

    assert result == "Código de moeda inválido. Use ('EUR', 'USD', 'BTC')"


def test_moeda_erro_na_URL():
    result = cotacao('\x11')

    assert result == "Código de moeda inválido. Use ('EUR', 'USD', 'BTC')"


def test_erro_conexao(respx_mock):
    # Arange
    respx_mock.get(URL_COTACAO.format('USD-BRL')).mock(
        side_effect=httpx.ConnectError
    )

    # Act
    result = cotacao('USD')

    # Assert
    assert result == 'Erro de conexão, tente mais tarde.'


def test_erro_timeout(respx_mock):
    # Arange
    respx_mock.get(URL_COTACAO.format('USD-BRL')).mock(
        side_effect=httpx.TimeoutException
    )

    # Act
    result = cotacao('USD')

    # Assert
    assert result == 'Erro de conexão, tente mais tarde.'
