from pathlib import Path

from softcom_selfhost_automation.config import Environment, Settings, load_settings


def test_carrega_perfil_desktop() -> None:
    config_dir = Path(__file__).resolve().parents[2] / "config"

    settings = load_settings("desktop", config_dir)

    assert settings.environment is Environment.DESKTOP
    assert settings.openapi_url.endswith("/scalar/swagger/v1/swagger.json")


def test_url_do_dispositivo_habilita_autenticacao() -> None:
    settings = Settings(device_url="http://host:7711/device/add?client_id=public")

    assert settings.authentication_configured


def test_credenciais_dricaia_habilitam_autenticacao_especifica() -> None:
    settings = Settings(dricaia_email="teste@example.com", dricaia_password="segredo")

    assert settings.dricaia_credentials_configured


def test_variavel_de_restaurante_habilita_seus_endpoints() -> None:
    settings = Settings(restaurant_endpoints_enabled=True)

    assert settings.restaurant_tests_enabled


def test_configuracao_legada_de_mesas_continua_habilitando_restaurante() -> None:
    settings = Settings(mesas_database_enabled=True)

    assert settings.restaurant_tests_enabled
