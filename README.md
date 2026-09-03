# Softcom Selfhost Test Automation

Projeto de automação caixa-preta dos endpoints do Softcom Selfhost. A suíte
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
cd softcom-selfhost-automation
Copy-Item .env.example .env
uv sync --all-extras
```

Edite `.env` localmente. O arquivo não é versionado:

```dotenv
SELFHOST_ENVIRONMENT=desktop
SELFHOST_BASE_URL=http://localhost:7711
SELFHOST_DEVICE_URL=http://servidor:7711/device/add?client_id=...&empresa_name=...&empresa_cnpj=...&device_name=...

# Opcionais: habilitam os contratos da DricaIA e de Restaurante.
SELFHOST_DRICAIA_EMAIL=
SELFHOST_DRICAIA_PASSWORD=
SELFHOST_RESTAURANT_ENDPOINTS_ENABLED=false

# Proteção adicional para rotas de escrita.
SELFHOST_DESTRUCTIVE_TESTS_ENABLED=false
```

Mantenha a URL entre aspas se for defini-la diretamente no PowerShell, pois
`&` é um operador do shell. No arquivo `.env`, cole a URL sem aspas.

No perfil `desktop`, essa é a única informação de autenticação necessária. A
automação acrescenta um `device_id` único, cadastra o dispositivo, obtém
`client_id`/`client_secret` da resposta e gera o bearer token em
`/authentication/token`. Se a URL tiver um prefixo de relay, ele também é
preservado no endpoint do token.

`SELFHOST_CLIENT_ID` e `SELFHOST_CLIENT_SECRET` continuam disponíveis como
fallback para o perfil WEB ou para ambientes já cadastrados. Quando
`SELFHOST_DEVICE_URL` estiver preenchida, ela tem precedência.

As credenciais `SELFHOST_DRICAIA_EMAIL` e `SELFHOST_DRICAIA_PASSWORD` são usadas
somente pelos endpoints `/api/v2/dricaia/*`. A suíte realiza o login e mantém o
token da DricaIA separado do token do Selfhost.

Para incluir Restaurante, defina
`SELFHOST_RESTAURANT_ENDPOINTS_ENABLED=true`. Essa chave informa que o Selfhost
apontado pela URL do dispositivo já está com o módulo e o banco auxiliar de
mesas configurados. A automação não precisa das credenciais diretas desse banco
para testar o contrato HTTP. A variável legada
`SELFHOST_MESAS_DATABASE_ENABLED=true` continua aceita por compatibilidade.

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

Contratos de todos os endpoints V1 solicitados e de todos os endpoints V2 do Desktop:

```powershell
uv run pytest tests/contract/test_desktop_endpoints.py --environment desktop --run-api-tests
```

Sem `--run-api-tests`, os testes que acessariam o Selfhost são ignorados. Isso
permite executar `uv run pytest` localmente sem depender de um ambiente ativo.

Por segurança, métodos de escrita (`POST`, `PUT`, `PATCH` e `DELETE`) ficam
separados e desabilitados. Mesmo habilitados, os testes de contrato enviam uma
requisição sem payload para validar rota, autenticação e envelope sem criar uma
massa válida:

```powershell
$env:SELFHOST_DESTRUCTIVE_TESTS_ENABLED = "true"
uv run pytest tests/contract/test_desktop_endpoints.py --environment desktop --run-api-tests --run-destructive-tests
```

Os dois controles são obrigatórios para executar rotas de escrita: a variável
no `.env` e a opção `--run-destructive-tests` no comando. Testes funcionais que
efetivamente criam ou alteram registros devem usar massa conhecida e limpeza
explícita.

## O que o teste de contrato valida

O teste não compara o JSON completo com um arquivo estático. Ele faz a chamada
real ao endpoint e valida:

- que o verbo é aceito pela rota (não retorna `405`); um `404` com contrato
  válido é aceito quando o ID de amostra não existe na base;
- que não ocorreu erro interno (`status < 500`);
- que o tipo de conteúdo e a estrutura básica correspondem à versão da API;
- que os campos obrigatórios do envelope possuem tipos válidos, quando houver.

A suíte considera o contrato real de cada versão:

- V1: envelope legado (`code`, `message`, `human` e `data`), exceto `ApiStatus`,
  que retorna conteúdo HTML/JSON sem envelope;
- V2: objeto JSON do recurso ou paginação (`data`, `current_page`, `meta`, etc.),
  conforme o endpoint; `healthcheck` retorna conteúdo sem envelope;
- DricaIA V2 usa um token separado, obtido automaticamente quando
  `SELFHOST_DRICAIA_EMAIL` e `SELFHOST_DRICAIA_PASSWORD` estão configurados.

Essas verificações não validam regras de negócio, valores exatos retornados ou
persistência no banco de dados. Esses comportamentos pertencem aos testes
funcionais e de workflow.

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

## Cobertura atual

A suíte Desktop cataloga **138 operações HTTP**: **73 V1** e **65 V2**. Dessas,
93 são classificadas como seguras e 45 como potencialmente destrutivas.

Na V1, estão cobertos os domínios solicitados:

- ApiStatus;
- Balanço;
- Catraca;
- Clientes;
- Empresa;
- Grupos;
- Produtos;
- Promoção;
- Restaurante;
- Vendas;
- Vendas360Webhook;
- Vendedores;
- Vínculos Fiscais.

Na V2, estão catalogados todos os controllers disponíveis no Desktop:

- Balanço, Catraca, Clientes, Device, DricaIA, Empresa e Financeiro;
- Funcionários, Grupos, Healthcheck, Movimentação e NFe/NFCe;
- Produtos, Promoção, Restaurante, Vendas e Vínculos Fiscais.

Rotas parametrizadas usam valores de amostra seguros para exercitar o contrato.
Fluxos funcionais com persistência continuam separados, pois precisam de massa
conhecida e limpeza explícita por domínio.
