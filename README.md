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

### Script interativo para Windows

O arquivo `run_tests.ps1` centraliza a execução da suíte. Ele:

- permite selecionar o ambiente Desktop ou WEB;
- solicita e valida a URL completa do dispositivo;
- permite habilitar testes destrutivos, exigindo uma segunda confirmação;
- mostra cada teste como `PASSED`, `FAILED` ou `SKIPPED`;
- salva os resultados em `allure-results/`;
- gera `allure-report/` e abre o relatório no navegador padrão.

Para iniciar o modo interativo:

```powershell
.\run_tests.ps1
```

O script exige o `uv` e instala/carrega automaticamente o extra Python
`report`, necessário para o argumento `--alluredir`. Para gerar o relatório,
usa o Allure CLI instalado
no `PATH`; caso ele não esteja disponível, usa `npx` para executar o pacote
`allure-commandline`. É necessário ter Java instalado para o Allure.

Também é possível executar sem perguntas. Exemplo seguro no Desktop:

```powershell
.\run_tests.ps1 -Environment desktop -DeviceUrl "http://servidor:7711/device/add?client_id=..." -NoDestructive
```

Exemplo com testes destrutivos (a confirmação ainda será solicitada):

```powershell
.\run_tests.ps1 -Environment desktop -DeviceUrl "http://servidor:7711/device/add?client_id=..." -Destructive
```

Parâmetros disponíveis:

| Parâmetro | Descrição |
| --- | --- |
| `-Environment desktop|web` | Define o ambiente sem abrir a seleção interativa. |
| `-DeviceUrl "..."` | Informa a URL do dispositivo sem solicitá-la no terminal. |
| `-NoDestructive` | Executa somente os testes seguros. |
| `-Destructive` | Inclui as rotas de escrita e solicita confirmação. |

Não combine `-Destructive` com `-NoDestructive`. No PowerShell, mantenha a URL
entre aspas porque ela normalmente contém `&`. O script define as variáveis
somente no processo atual e não grava a URL no `.env`.

No Desktop, executa o catálogo de contratos V1 e V2. No WEB, executa os
testes marcados como API que não sejam exclusivos do Desktop. Mesmo quando há
falhas, o script tenta gerar o relatório e encerra com o código retornado pelo
Pytest.

### Execução manual

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
real ao endpoint e verifica disponibilidade, autenticação e a estrutura mínima
da resposta. A validação aplicada depende do contrato registrado para cada
operação no catálogo.

### Validações HTTP comuns

- o método HTTP catalogado é aceito; uma resposta `405 Method Not Allowed`
  reprova o teste;
- a API não pode responder com erro interno: qualquer status `500` ou superior
  reprova o teste;
- rotas parametrizadas utilizam IDs, páginas, datas e filtros de amostra;
- um `404` pode ser aceito nas consultas por identificador inexistente, desde
  que a resposta ainda respeite o contrato JSON esperado;
- endpoints de status são mais rígidos: não podem responder `404` ou `405` e
  precisam retornar algum conteúdo.

### Contrato V1

Na maioria das operações V1, a resposta deve ser um objeto JSON com o envelope
legado:

```json
{
  "code": 0,
  "message": null,
  "human": null,
  "data": {}
}
```

A suíte valida que:

- o `Content-Type` começa com `application/json`;
- a raiz da resposta é um objeto JSON, e não uma lista ou valor simples;
- `code`, `message`, `human` e `data` estão presentes;
- `code` é número ou texto;
- `message` e `human` são texto ou `null`.

`ApiStatus` é uma exceção e aceita HTML ou JSON sem envelope, desde que haja
conteúdo. As operações `/api/balanco` e
`/api/produtos/produtos/collector` também são exceções: retornam objeto JSON
paginado sem o envelope legado e são validadas como tal.

### Contrato V2 e paginação

As operações V2 devem ser um objeto JSON e declarar `Content-Type` iniciado por
`application/json`. A estrutura pode ser o próprio recurso, um objeto de erro
válido para uma amostra inexistente ou uma resposta paginada.

Nas rotas paginadas, a suíte envia valores pequenos e determinísticos, em geral
`page=1` e `per_page=10`. Na V1, também exercita variantes em que a página faz
parte do caminho, como `/page/1` e `/page/1/10`. As respostas reais podem
conter `data` e metadados como `current_page`, `per_page`, `last_page`, `total`,
`links` ou `meta`.

Isso confirma que a API aceita os parâmetros de paginação e devolve um objeto
JSON. Atualmente, a suíte não compara os valores exatos de total, quantidade de
páginas ou links, pois eles dependem da massa existente em cada base.

`Healthcheck` é uma exceção e aceita conteúdo sem envelope JSON.

### Autenticação

- a URL do dispositivo é validada como HTTP(S) e deve apontar para
  `/device/add`;
- a automação acrescenta um `device_id` único, cadastra o dispositivo e exige
  que a resposta forneça `client_id` e `client_secret`;
- as credenciais são trocadas por um bearer token em `/authentication/token`;
- o token deve existir, ter tipo `Bearer` e tempo de expiração positivo;
- o `resources.url_base` retornado pelo Selfhost é normalizado, removendo query
  string e `/device/add`, mas preservando um eventual prefixo de relay;
- a DricaIA usa autenticação separada: a suíte chama
  `POST /api/v2/dricaia/login`, extrai `data.token` e usa esse novo token apenas
  nas operações `/api/v2/dricaia/*`.

Também existe um teste negativo que envia `grant_type=password` com credenciais
inválidas e espera o código de contrato `64` com a mensagem
`Unsupported grant_type`.

### Segurança e seleção de testes

- operações `GET` são classificadas como seguras;
- operações `POST`, `PUT`, `PATCH` e `DELETE` são classificadas como
  destrutivas, exceto autenticações e healthchecks tratados explicitamente;
- rotas destrutivas só executam quando
  `SELFHOST_DESTRUCTIVE_TESTS_ENABLED=true` e `--run-destructive-tests` são
  fornecidos;
- o teste de contrato chama as rotas de escrita sem payload válido para
  exercitar rota, autenticação e tratamento da requisição, sem montar uma massa
  persistível;
- Restaurante só executa quando
  `SELFHOST_RESTAURANT_ENDPOINTS_ENABLED=true`;
- testes exclusivos de Desktop ou WEB são ignorados no ambiente incompatível;
- testes internos impedem método/rota duplicados, exigem `sample_path` para
  rotas parametrizadas e verificam que as operações de escrita estejam marcadas
  como destrutivas.

### OpenAPI e smoke tests

Além do catálogo de endpoints, a suíte verifica que:

- o healthcheck e seu endpoint de informações respondem `200` e possuem
  conteúdo;
- o documento OpenAPI responde `200`;
- o documento contém uma versão `openapi` ou `swagger`, possui `paths` e
  documenta `/api/v2/healthcheck`.

Essas verificações não validam valores de negócio, quantidade exata de
registros, conteúdo integral de cada recurso nem persistência no banco de
dados. Esses comportamentos pertencem aos testes funcionais e de workflow, que
exigem massa conhecida e limpeza explícita.

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
schemas/                                baselines OpenAPI V1 e V2 versionados
scripts/                                manutenção explícita dos baselines
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

O workflow [`.github/workflows/quality.yml`](.github/workflows/quality.yml) executa
automaticamente essas verificações e todos os testes offline em cada `push`, pull
request ou acionamento manual no GitHub Actions. Ele não acessa o Selfhost, não
carrega o `.env` e não precisa de secrets. Os testes que exigem `--run-api-tests`
permanecem ignorados nessa etapa.

As falhas conhecidas da execução contra o ambiente Desktop e as tarefas propostas
estão registradas em [`docs/TESTS_PENDING.md`](docs/TESTS_PENDING.md).

Nos contratos V1 e V2, cada resposta também é validada contra o schema da operação
publicado no OpenAPI correspondente. A validação percorre objetos e listas, confere
tipos, campos obrigatórios, nulabilidade e formatos. Valores voláteis, como IDs,
datas e tokens, não são comparados literalmente: seu tipo e formato continuam sendo
verificados. Campos adicionais são tolerados para preservar a compatibilidade do
Selfhost; campos documentados com tipo incorreto causam falha com o caminho JSON do
campo divergente. Exceções legadas ausentes no OpenAPI continuam cobertas pelas
validações estruturais existentes.

Exemplo de falha produzida pela validação tipada:

```text
Resposta incompatível com o OpenAPI em GET /api/v2/clientes/contato (HTTP 200):
- $.per_page: '10' is not of type 'integer'
```

Os schemas não são derivados das respostas da própria execução. A fonte de verdade
dos testes é o baseline aprovado e versionado em `schemas/v1.openapi.json` e
`schemas/v2.openapi.json`. A suíte também compara esses arquivos com os documentos
publicados em `/scalar/swagger/v1/swagger.json` e
`/scalar/swagger/v2/swagger.json`. Dessa forma, mesmo que resposta e documentação
mudem juntas sem aviso, a diferença em relação à versão anterior é detectada.

Uma divergência deve ser classificada como bug ou evolução prevista antes da
atualização do baseline. Depois da aprovação, atualize os arquivos com:

```powershell
uv run python scripts/update_openapi_baselines.py --environment desktop
```

Revise o diff gerado antes do commit. A URL presente em `servers` é removida do
snapshot para não versionar informações específicas do ambiente.

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
