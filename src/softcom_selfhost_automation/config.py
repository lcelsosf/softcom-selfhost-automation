from __future__ import annotations

import tomllib
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Environment(StrEnum):
    DESKTOP = "desktop"
    WEB = "web"


class Settings(BaseSettings):
    """Configuracao efetiva de uma execucao da automacao."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SELFHOST_",
        extra="ignore",
        case_sensitive=False,
    )

    environment: Environment = Environment.DESKTOP
    base_url: AnyHttpUrl = "http://localhost:7711"  # type: ignore[assignment]
    device_url: AnyHttpUrl | None = None
    client_id: str = ""
    client_secret: str = ""
    dricaia_email: str = ""
    dricaia_password: str = ""
    verify_ssl: bool = True
    request_timeout: float = Field(default=30.0, gt=0)
    openapi_path: str = "/scalar/swagger/v1/swagger.json"
    restaurant_endpoints_enabled: bool = False
    mesas_database_enabled: bool = False
    destructive_tests_enabled: bool = False

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Variáveis seguras da pipeline devem prevalecer sobre os defaults TOML.
        return env_settings, dotenv_settings, init_settings, file_secret_settings

    @property
    def openapi_url(self) -> str:
        return f"{str(self.base_url).rstrip('/')}/{self.openapi_path.lstrip('/')}"

    @property
    def credentials_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    @property
    def authentication_configured(self) -> bool:
        """A URL do dispositivo tem precedencia sobre credenciais manuais."""

        return self.device_url is not None or self.credentials_configured

    @property
    def dricaia_credentials_configured(self) -> bool:
        return bool(self.dricaia_email and self.dricaia_password)

    @property
    def restaurant_tests_enabled(self) -> bool:
        """Aceita a chave atual e a configuração legada do banco de mesas."""

        return self.restaurant_endpoints_enabled or self.mesas_database_enabled


def load_settings(environment: str, config_dir: Path | None = None) -> Settings:
    """Carrega defaults TOML e permite sobrescrita por SELFHOST_* ou .env."""

    root = config_dir or Path(__file__).resolve().parents[2] / "config"
    profile_path = root / f"{environment}.toml"
    if not profile_path.exists():
        raise ValueError(f"Ambiente desconhecido: {environment!r}")

    with profile_path.open("rb") as profile:
        profile_data: dict[str, Any] = tomllib.load(profile)

    return Settings(**profile_data)
