from unittest.mock import Mock, patch

import httpx

from softcom_selfhost_automation.clients import AuthenticationClient


def test_gera_token_a_partir_da_url_do_dispositivo() -> None:
    api = Mock()
    api.post_url.side_effect = [
        httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "client_id": "id",
                    "client_secret": "secret",
                    "resources": {"url_base": "http://api-host:7711/prefix/"},
                },
            },
        ),
        httpx.Response(
            200,
            json={"code": 0, "data": {"token": "jwt", "type": "Bearer", "expires_in": 3600}},
        ),
    ]
    api.parse_envelope.side_effect = lambda response: response.json()

    with patch("softcom_selfhost_automation.clients.authentication.uuid4") as uuid:
        uuid.return_value.hex = "1234567890abcdef"
        authentication = AuthenticationClient(api).create_authentication_from_device_url(
            "http://host:7711/device/add?client_id=public&empresa_name=MATRIZ&device_name=Teste"
        )

    registration_url = api.post_url.call_args_list[0].args[0]
    assert "device_id=PYTEST_AUTOMACAO_1234567890ab" in registration_url
    assert api.post_url.call_args_list[1].args[0] == "http://host:7711/authentication/token"
    assert api.post_url.call_args_list[1].kwargs["data"] == {
        "grant_type": "client_credentials",
        "client_id": "id",
        "client_secret": "secret",
    }
    assert authentication.token.value == "jwt"
    assert authentication.api_base_url == "http://api-host:7711/prefix"


def test_preserva_prefixo_do_relay_ao_gerar_token() -> None:
    registration_url, token_base_url = AuthenticationClient._prepare_device_registration(
        "https://relay.example/abc/device/add?client_id=public&device_name=Teste"
    )

    assert registration_url.startswith("https://relay.example/abc/device/add?")
    assert token_base_url == "https://relay.example/abc"
