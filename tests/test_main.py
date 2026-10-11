from http import HTTPStatus

import pytest
from samsungtvws.exceptions import (
    ConnectionFailure,
    HttpApiError,
    MessageError,
    ResponseError,
    UnauthorizedError,
)
from websocket import WebSocketException

from samsung_remote.main import KEYS, app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_renders_remote(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert b"Samsung TV Remote" in response.data


def test_unknown_key_returns_404(client):
    response = client.post("/key/nope")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.get_json() == {"error": "unknown key"}


@pytest.mark.parametrize("name", sorted(KEYS))
def test_known_key_is_sent_to_the_tv(client, mocker, name):
    tv = mocker.patch("samsung_remote.main.SamsungTVWS").return_value

    response = client.post(f"/key/{name}")

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"ok": True}
    tv.send_key.assert_called_once_with(KEYS[name])


@pytest.mark.parametrize(
    "error",
    [
        OSError("unreachable"),
        ConnectionFailure("refused"),
        UnauthorizedError("not allowed"),
        HttpApiError("bad api call"),
        MessageError("bad message"),
        ResponseError("bad response"),
        WebSocketException("handshake failed"),
    ],
    ids=lambda error: type(error).__name__,
)
def test_tv_failure_returns_500(client, mocker, error):
    mocker.patch("samsung_remote.main.SamsungTVWS", side_effect=error)

    response = client.post("/key/power")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.get_json() == {"error": str(error)}
