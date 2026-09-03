# Baselines OpenAPI

Os arquivos `v1.openapi.json` e `v2.openapi.json` são snapshots versionados dos
contratos aprovados. Os testes de resposta usam esses arquivos, e não o documento
dinâmico publicado pelo ambiente, para conferir campos, tipos, nulabilidade, listas,
objetos aninhados e formatos.

A suíte também compara o OpenAPI publicado pelo ambiente com esses snapshots. Uma
divergência deve ser classificada antes de qualquer atualização:

- **bug:** aplicação ou documentação mudou sem representar um contrato aprovado;
- **evolução prevista:** mudança revisada que exige atualização do baseline e,
  quando necessário, dos consumidores da API.

Para atualizar conscientemente os dois arquivos após a aprovação:

```powershell
uv run python scripts/update_openapi_baselines.py --environment desktop
```

Revise o diff integral antes do commit. O script remove somente `servers`, porque a
URL contém dados próprios do ambiente; operações e schemas permanecem intactos.
