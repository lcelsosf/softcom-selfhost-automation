from pathlib import Path

from softcom_selfhost_automation.config import Environment, load_settings


def test_carrega_perfil_desktop() -> None:
    config_dir = Path(__file__).resolve().parents[2] / "config"

    settings = load_settings("desktop", config_dir)

    assert settings.environment is Environment.DESKTOP
    assert settings.openapi_url.endswith("/scalar/swagger/v1/swagger.json")
