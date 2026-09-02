# Softcom Selfhost Test Automation

Projeto de automação caixa-preta dos endpoints do Softcom Selfhost. A mesma suíte
atende aos perfis:

- `desktop`: Selfhost integrado ao ERP Desktop/SQL Server;
- `web`: Selfhost encaminhando as operações ao ERP WEB/SoftcomShop/MySQL.

As rotas expostas não são necessariamente suportadas pelos dois ERPs. A matriz
inicial está em `src/softcom_selfhost_automation/capabilities.py` e deve ser
atualizada sempre que uma regra de compatibilidade mudar.

## Requisitos

- Python 3.12 ou superior;
- `uv` instalado;
- uma instância exclusiva do Selfhost para testes funcionais/destrutivos.

Os adaptadores opcionais de banco requerem também:

- Microsoft ODBC Driver 18 para SQL Server;
- conectividade com o MySQL do ambiente de automação.

## Preparação

```powershell
cd softcom-selfhost-test-automation
Copy-Item .env.example .env
uv sync --all-extras
```

Edite `.env` localmente. O arquivo não é versionado:

```dotenv
SELFHOST_ENVIRONMENT=desktop
SELFHOST_BASE_URL=http://localhost:7711
SELFHOST_CLIENT_ID=client-id-do-ambiente-de-automacao
SELFHOST_CLIENT_SECRET=client-secret-do-ambiente-de-automacao
```

As variáveis `SELFHOST_*` têm precedência sobre os arquivos em `config/`.

## Execução

Testes unitários do próprio projeto, sem acessar a API:

```powershell
uv run pytest
```

Smoke no Desktop:

```powershell
uv run pytest -m smoke --environment desktop --run-api-tests
```

Smoke no WEB:

```powershell
uv run pytest -m smoke --environment web --run-api-tests
```

Contrato OpenAPI:

```powershell
uv run pytest -m contract --environment desktop --run-api-tests
```

Em paralelo, somente quando a massa de dados for isolada:

```powershell
uv run pytest -n auto -m "smoke or contract" --environment desktop --run-api-tests
```

O documento OpenAPI esperado está em:

```text
/scalar/swagger/v1/swagger.json
```

## Estrutura

```text
config/                                 perfis sem segredos
src/softcom_selfhost_automation/
├── assertions/                         validações reutilizáveis
├── builders/                           construção de massas
├── clients/                            clientes HTTP por domínio
├── database/                           setup/cleanup auxiliar de banco
├── models/                             requests e responses tipados
├── capabilities.py                     matriz ERP × endpoint
└── config.py                            configuração efetiva
tests/
├── authentication/
├── contract/
├── functional/
├── smoke/
├── unit/
└── workflows/
```

## Convenções

- Organize os testes pelo domínio de negócio, não pelo verbo HTTP.
- Valide o status HTTP e o envelope (`code`, `message`, `human`, `data`).
- Use a API para a asserção principal; banco direto serve somente para massa,
  limpeza ou efeitos que não possam ser consultados pela API.
- Todo dado criado deve receber um identificador único da execução.
- Não compartilhe empresa, estoque ou sequência de venda entre testes paralelos.
- Marque cenários que alterem estado com `@pytest.mark.destructive`.
- Marque exceções por ambiente com `desktop`, `web` ou `restaurant`.

## Qualidade

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Relatório JUnit para CI:

```powershell
uv run pytest --junitxml=reports/junit.xml --environment desktop --run-api-tests
```

Relatório Allure:

```powershell
uv run pytest --alluredir=allure-results --environment desktop --run-api-tests
```

## Próximos domínios

A implementação inicial cobre healthcheck, obtenção de token e disponibilidade
do OpenAPI. A evolução recomendada é:

1. clientes v2;
2. produtos v2;
3. vendas v2;
4. fluxos completos de venda;
5. contratos gerados com Schemathesis, filtrados pela matriz de capacidades.
