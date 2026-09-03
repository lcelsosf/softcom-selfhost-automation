import httpx
import pytest

from softcom_selfhost_automation.assertions.openapi import assert_response_matches_openapi


def _document(schema: dict[str, object]) -> dict[str, object]:
    return {
        "openapi": "3.0.1",
        "info": {"title": "Test", "version": "1"},
        "paths": {
            "/items": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {"application/json": {"schema": schema}},
                        }
                    }
                }
            }
        },
    }


def _response(payload: object) -> httpx.Response:
    return httpx.Response(
        200,
        json=payload,
        request=httpx.Request("GET", "https://example.test/items"),
    )


def test_valida_tipos_e_campos_obrigatorios() -> None:
    document = _document(
        {
            "type": "object",
            "required": ["id", "active"],
            "properties": {"id": {"type": "integer"}, "active": {"type": "boolean"}},
        }
    )

    assert_response_matches_openapi(_response({"id": 1, "active": True}), document, "GET", "/items")


def test_informa_caminho_do_tipo_incorreto_sem_comparar_valor_volatil() -> None:
    document = _document(
        {
            "type": "object",
            "required": ["id", "created_at"],
            "properties": {
                "id": {"type": "integer"},
                "created_at": {"type": "string", "format": "date-time"},
            },
        }
    )

    with pytest.raises(AssertionError, match=r"\$\.id: '1' is not of type 'integer'"):
        assert_response_matches_openapi(
            _response({"id": "1", "created_at": "2026-09-03T12:00:00Z"}),
            document,
            "GET",
            "/items",
        )


def test_aceita_valores_volateis_diferentes_quando_tipo_e_formato_sao_validos() -> None:
    document = _document(
        {
            "type": "object",
            "properties": {
                "token": {"type": "string", "minLength": 1},
                "created_at": {"type": "string", "format": "date-time"},
            },
        }
    )

    assert_response_matches_openapi(
        _response({"token": "outro-token", "created_at": "2026-09-03T15:42:00Z"}),
        document,
        "GET",
        "/items",
    )


def test_falha_quando_status_nao_esta_documentado() -> None:
    response = httpx.Response(
        404,
        json={"message": "missing"},
        request=httpx.Request("GET", "https://example.test/items"),
    )

    with pytest.raises(AssertionError, match="Status HTTP 404 não está documentado"):
        assert_response_matches_openapi(response, _document({"type": "object"}), "GET", "/items")


def test_aceita_status_nao_documentado_quando_excecao_e_explicita() -> None:
    response = httpx.Response(
        404,
        json={"message": "missing"},
        request=httpx.Request("GET", "https://example.test/items"),
    )

    assert_response_matches_openapi(
        response,
        _document({"type": "object"}),
        "GET",
        "/items",
        allow_undocumented_status=True,
    )


def test_resolve_referencia_local_em_components() -> None:
    document = _document({"$ref": "#/components/schemas/Item"})
    document["components"] = {
        "schemas": {
            "Item": {
                "type": "object",
                "required": ["id"],
                "properties": {"id": {"type": "integer"}},
            }
        }
    }

    with pytest.raises(AssertionError, match=r"\$\.id: '1' is not of type 'integer'"):
        assert_response_matches_openapi(_response({"id": "1"}), document, "GET", "/items")


def test_adapta_camel_case_e_nullable_do_openapi_para_json_real() -> None:
    document = _document({"$ref": "#/components/schemas/Item"})
    document["components"] = {
        "schemas": {
            "Item": {
                "type": "object",
                "required": ["createdAt"],
                "properties": {
                    "createdAt": {"type": "string"},
                    "displayName": {"type": "string", "nullable": True},
                },
                "additionalProperties": False,
            }
        }
    }

    assert_response_matches_openapi(
        _response({"created_at": "2026-09-03", "display_name": None}),
        document,
        "GET",
        "/items",
    )


def test_pode_ignorar_operacao_legada_ausente_no_openapi() -> None:
    assert_response_matches_openapi(
        _response({"id": 1}),
        _document({"type": "object"}),
        "GET",
        "/legacy",
        allow_undocumented_operation=True,
    )
