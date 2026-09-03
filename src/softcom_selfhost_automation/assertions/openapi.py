from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import httpx
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

JsonObject = Mapping[str, Any]


def assert_response_matches_openapi(
    response: httpx.Response,
    document: JsonObject,
    method: str,
    path: str,
    *,
    allow_undocumented_status: bool = False,
    allow_undocumented_operation: bool = False,
) -> None:
    """Valida corpo, tipos e formatos usando o schema OpenAPI da operação."""

    operation = _operation(document, method, path, optional=allow_undocumented_operation)
    if operation is None:
        return
    response_spec = _response_spec(
        operation, response.status_code, allow_undocumented_status=allow_undocumented_status
    )
    if response_spec is None:
        return
    schema = _response_schema(response_spec, response.headers.get("content-type", ""))
    if schema is None:
        # 204 e respostas de erro sem corpo/schema são contratos válidos no OpenAPI.
        if response.status_code not in {204, 404} and response.content:
            assert response_spec.get("content") is not None, (
                f"{method.upper()} {path}: resposta {response.status_code} possui corpo, mas o "
                "OpenAPI não declara conteúdo"
            )
        return

    try:
        payload = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"{method.upper()} {path}: resposta {response.status_code} não contém JSON válido"
        ) from exc

    try:
        validation_schema = _normalize_schema(schema, document)
        validator = Draft202012Validator(validation_schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
    except SchemaError as exc:
        raise AssertionError(
            f"Schema OpenAPI inválido para {method.upper()} {path}: {exc}"
        ) from exc

    if errors:
        details = "\n".join(f"- {_format_error(error)}" for error in errors[:10])
        raise AssertionError(
            f"Resposta incompatível com o OpenAPI em {method.upper()} {path} "
            f"(HTTP {response.status_code}):\n{details}"
        )


def _operation(
    document: JsonObject, method: str, path: str, *, optional: bool
) -> JsonObject | None:
    paths = document.get("paths")
    operation = paths.get(path, {}).get(method.lower()) if isinstance(paths, Mapping) else None
    if operation is None and optional:
        return None
    assert isinstance(operation, Mapping), (
        f"Operação {method.upper()} {path} não encontrada no documento OpenAPI"
    )
    return operation


def _response_spec(
    operation: JsonObject,
    status_code: int,
    *,
    allow_undocumented_status: bool,
) -> JsonObject | None:
    responses = operation.get("responses")
    assert isinstance(responses, Mapping), "Operação OpenAPI não declara responses"

    exact = responses.get(str(status_code))
    wildcard = responses.get(f"{status_code // 100}XX")
    response_spec = exact or wildcard or responses.get("default")
    if response_spec is None and allow_undocumented_status:
        return None
    assert isinstance(response_spec, Mapping), (
        f"Status HTTP {status_code} não está documentado no OpenAPI; "
        f"documentados: {sorted(str(item) for item in responses)}"
    )
    return response_spec


def _response_schema(response_spec: JsonObject, content_type: str) -> JsonObject | None:
    content = response_spec.get("content")
    if not isinstance(content, Mapping) or not content:
        return None

    media_type = content_type.partition(";")[0].strip().lower()
    media = content.get(media_type) or content.get("application/json")
    if not isinstance(media, Mapping):
        media = next((item for item in content.values() if isinstance(item, Mapping)), None)
    if not isinstance(media, Mapping):
        return None

    schema = media.get("schema")
    return schema if isinstance(schema, Mapping) and schema else None


def _normalize_schema(schema: JsonObject, document: JsonObject) -> dict[str, Any]:
    """Adapta OpenAPI 3.0/C# à serialização JSON real em snake_case."""

    normalized = dict(_normalize_node(schema))
    components = document.get("components", {})
    normalized_components = _normalize_node(components) if isinstance(components, Mapping) else {}
    normalized.setdefault("components", normalized_components)
    _allow_response_extensions(normalized)
    return normalized


def _normalize_node(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalize_node(item) for item in value]
    if not isinstance(value, Mapping):
        return value

    normalized = {key: _normalize_node(item) for key, item in value.items() if key != "nullable"}
    properties = normalized.get("properties")
    if isinstance(properties, Mapping):
        normalized["properties"] = {_snake_case(str(key)): item for key, item in properties.items()}
    required = normalized.get("required")
    if isinstance(required, list):
        normalized["required"] = [_snake_case(str(item)) for item in required]

    # nullable é uma extensão do OpenAPI 3.0, não do JSON Schema 2020-12.
    if value.get("nullable") is True:
        declared_type = normalized.get("type")
        if isinstance(declared_type, str):
            normalized["type"] = [declared_type, "null"]
        elif "$ref" in normalized:
            reference = normalized.pop("$ref")
            normalized["anyOf"] = [{"$ref": reference}, {"type": "null"}]
    return normalized


def _snake_case(name: str) -> str:
    first_pass = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first_pass).lower()


def _allow_response_extensions(schema: Any) -> None:
    """Campos extras são aceitos; campos documentados continuam com tipo estrito."""

    if isinstance(schema, list):
        for item in schema:
            _allow_response_extensions(item)
        return
    if not isinstance(schema, dict):
        return
    if schema.get("type") == "object" or "properties" in schema:
        schema["additionalProperties"] = True
    for value in schema.values():
        _allow_response_extensions(value)


def _format_error(error: ValidationError) -> str:
    location = "$"
    for part in error.absolute_path:
        location += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{location}: {error.message}"
