# Testes pendentes

Este documento registra as falhas encontradas na execução segura dos contratos
Desktop em 3 de setembro de 2026. Ele não contém credenciais nem a URL do
ambiente.

Resultado de referência:

```text
67 passed, 19 failed, 45 skipped, 7 errors
```

Os 45 testes ignorados são operações potencialmente destrutivas e não representam
falhas. Antes de alterar a automação, cada divergência abaixo deve ser comparada com
a documentação/OpenAPI e com uma resposta obtida usando massa de dados conhecida.

Após a validação tipada por OpenAPI ser habilitada, a execução também passa a
evidenciar divergências de tipos e formatos descritas em TP-006.

## Pendências mapeadas

### TP-001 — Corrigir autenticação da DricaIA

Prioridade: alta. Categoria: ambiente/autenticação.

O login `POST /api/v2/dricaia/login` respondeu `401 Unauthorized`. Como o token
específico não foi obtido, os seis contratos dependentes também terminaram com erro:

- `GET /api/v2/dricaia/customer`
- `GET /api/v2/dricaia/enterprises`
- `GET /api/v2/dricaia/financial`
- `GET /api/v2/dricaia/purchases`
- `GET /api/v2/dricaia/sales`
- `GET /api/v2/dricaia/stock`

Tarefas:

- confirmar que o e-mail existe em `DricaIAUsers` no ambiente testado;
- confirmar a senha BCrypt e eventuais requisitos de usuário ativo;
- validar manualmente o payload `{ "email": "...", "password": "..." }`;
- repetir a suíte e confirmar que o token retornado em `data.token` autentica as
  seis rotas.

Critério de aceite: login bem-sucedido, token separado do token Selfhost e os seis
contratos executados sem erro de autenticação.

### TP-002 — Revisar contratos V1 de Restaurante

Prioridade: alta. Categoria: automação/contrato.

Algumas rotas retornaram JSON válido, mas em formato diferente do envelope V1
`code/message/human/data` configurado no catálogo:

- `GET /api/restaurantes/configuracao` — retornou objeto de configuração direto;
- `GET /api/restaurantes/mesa` — retornou lista direta;
- `GET /api/restaurantes/mesa/adiantamento/{id}` — retornou lista direta;
- `GET /api/restaurantes/mesa/{id}/concorrencia/status` — retornou objeto direto;
- `GET /api/restaurantes/dricaia` — retornou objeto de resumo direto.

Tarefas:

- conferir na documentação se essas exceções V1 são intencionais;
- criar/atribuir contratos explícitos de objeto ou lista JSON no catálogo;
- adicionar testes unitários para impedir regressão desses contratos especiais.

Critério de aceite: contrato configurado de acordo com a documentação e respostas
reais aceitas sem flexibilizar globalmente o envelope V1.

### TP-003 — Usar massa válida nas rotas parametrizadas

Prioridade: alta. Categoria: automação/massa de teste.

Os valores de amostra estáticos não representam necessariamente registros existentes:

- `GET /api/produtos/grupos/{id}` — retornou “Não Encontrado”;
- `GET /api/restaurantes/auth/mesa/{id}` — erro por referência nula;
- `GET /api/restaurantes/produto/combo/{id}` — resposta incompatível;
- `GET /api/produtos/vinculosfiscais/{id}` — erro por referência nula;
- `GET /api/v2/restaurantes/auth/mesa/{id}` — respondeu `500`;
- `GET /api/v2/restaurantes/produto/combo/{id}` — respondeu `500`.

Tarefas:

- obter IDs existentes a partir das respectivas rotas de listagem;
- disponibilizar esses IDs por fixtures de sessão;
- definir comportamento explícito quando a listagem estiver vazia (skip com motivo
  ou validação documentada de `404`);
- não tratar respostas `500` como ausência normal de massa.

Critério de aceite: rotas usam IDs reais e distinguem corretamente recurso ausente
de falha interna.

### TP-004 — Corrigir consultas incompatíveis com o banco Desktop

Prioridade: alta. Categoria: backend/banco de dados.

As seguintes rotas apresentaram erro interno relacionado à execução de consultas:

- `GET /api/produtos/produtos/{id}` — consulta referencia colunas inexistentes,
  incluindo `Desativado`, `NaoVender`, `PercentualICMS`, `PMC`, `STIPI_Entrada`,
  `IPI`, campos de PIS/COFINS e `Origem`;
- `GET /api/v2/clientes/clientes` — respondeu `500`;
- `GET /api/v2/clientes/clientes/ultima_sincronizacao/{timestamp}` — respondeu
  `500` com erro ao executar o comando;
- `GET /api/v2/financeiro/forma-pagamento` — respondeu `500`;
- `GET /api/v2/produtos/nfe/classificacao-tributaria` — respondeu `500`.

Tarefas:

- comparar a versão do schema do banco com a versão esperada pelo Selfhost;
- executar migrations/atualização do Desktop, se aplicável;
- capturar a inner exception e identificar a consulta de cada resposta `500`;
- corrigir consulta ou compatibilidade de versão no backend;
- repetir os contratos sem alterar a asserção que rejeita status `>=500`.

Critério de aceite: todas as rotas respondem abaixo de `500` e entregam o contrato
documentado.

### TP-005 — Diagnosticar respostas vazias ou incompatíveis

Prioridade: média. Categoria: documentação/massa/backend.

As rotas abaixo falharam sem informação suficiente para decidir se o problema é
contrato incorreto, massa ausente ou implementação da API:

- `GET /api/restaurantes/produto/combo`
- `GET /api/vendedores/garcom`
- `GET /api/v2/restaurantes/produto/combo`

Tarefas:

- registrar status, headers e corpo integral em um ambiente sem dados sensíveis;
- comparar as respostas com OpenAPI e com a implementação do controller;
- cadastrar massa mínima de combo/garçom quando necessário;
- atualizar somente o contrato específico caso o formato real esteja documentado.

Critério de aceite: causa identificada e teste determinístico com massa presente ou
ausente.

### TP-006 — Alinhar respostas reais aos schemas OpenAPI V2

Prioridade: alta. Categoria: contrato/backend.

A validação tipada identificou divergências adicionais entre a documentação e a
serialização atual:

- `per_page` retorna `string` em diversas respostas paginadas, mas o schema declara
  `integer`;
- `GET /api/v2/clientes/financeiro/detalhe`,
  `GET /api/v2/empresa/empresas/{page}`, `GET /api/v2/financeiro/cartoes` e
  `GET /api/v2/restaurantes/mesa` retornam um objeto paginado enquanto seus schemas
  declaram um array;
- algumas propriedades e status de erro retornados pela API não estão documentados.

Tarefas:

- decidir, por rota, se o backend ou o OpenAPI representa o contrato correto;
- corrigir `per_page` para número ou documentar explicitamente a string;
- documentar o wrapper de paginação nas quatro rotas indicadas;
- documentar respostas `400` e `404` existentes;
- repetir a validação tipada até eliminar as divergências.

Critério de aceite: respostas reais validam campos documentados, tipos, nulabilidade,
arrays, objetos aninhados e formatos, sem comparar valores voláteis.

## Próximas suítes funcionais

Depois de resolver as divergências atuais, ainda devem ser implementadas tarefas de
maior escopo:

- criar fixtures isoladas para cliente, grupo, produto, vendedor, vínculo fiscal,
  mesa e combo;
- validar paginação com primeira página, próxima página, página vazia e limites;
- executar workflows de criação, consulta, alteração e exclusão com limpeza ao fim;
- comparar efeitos das escritas com a API e, quando indispensável, com o banco;
- habilitar os 45 testes destrutivos somente em uma base exclusiva;
- implementar posteriormente o workflow de CI para testes reais da API, usando
  secrets e execução manual.

## Como atualizar este documento

Após cada execução completa, registre a data e o resumo, remova somente os endpoints
que passaram de forma repetível e abra uma nova tarefa quando a causa de uma falha
for diferente das categorias existentes.
