from typing import Literal, TypeAlias, get_args
import httpx
import respx

URL_COTAÇÃO = 'https://economia.awesomeapi.com.br/json/last/{}'
Moeda: TypeAlias = Literal['EUR', 'USD', 'BTC']


def cotação(moeda: Moeda):
    code = f'{moeda}-BRL'
    try:
        response = httpx.get(URL_COTAÇÃO.format(code))
        data = response.json()[code.replace('-', '')]

        return f'Última cotação: {data['high']}'

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
    mocked_response = httpx.Response(
        200, json={'USDBRL': {'high': 5.7945}}
    )
    respx.get(
        URL_COTAÇÃO.format('USD-BRL')
    ).mock(mocked_response)

    # Act
    result = cotação('USD')

    # Assert
    assert result == 'Última cotação: 5.7945'


@respx.mock
def test_moeda_errada():
    mocked_response = httpx.Response(200, json={})

    respx.get(
        URL_COTAÇÃO.format('MDT-BRL')
    ).mock(mocked_response)

    result = cotação('MDT')

    assert (
        result == "Código de moeda inválido. Use ('EUR', 'USD', 'BTC')"
    )


def test_moeda_erro_na_URL():
    result = cotação('\x11')

    assert (
        result == "Código de moeda inválido. Use ('EUR', 'USD', 'BTC')"
    )


def test_erro_conexao(respx_mock):
    # Arange
    respx_mock.get(
        URL_COTAÇÃO.format('USD-BRL')
    ).mock(side_effect=httpx.ConnectError)

    # Act
    result = cotação('USD')

    # Assert
    assert result == 'Erro de conexão, tente mais tarde.'


def test_erro_timeout(respx_mock):
    # Arange
    respx_mock.get(
        URL_COTAÇÃO.format('USD-BRL')
    ).mock(side_effect=httpx.TimeoutException)

    # Act
    result = cotação('USD')

    # Assert
    assert result == 'Erro de conexão, tente mais tarde.'