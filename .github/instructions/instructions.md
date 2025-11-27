---
applyTo: "**"
---

# Diretrizes para o LLM — Projeto "robbot"

Forneça contexto do projeto e diretrizes de codificação que o modelo de IA deve seguir ao gerar código, responder perguntas ou revisar mudanças.

---

## Papel do LLM

- Objetivo: gerar/editar código seguindo a arquitetura definida em `project-root/src/robbot`.
- Regra principal: cada arquivo gerado deve ser colocado no diretório correto conforme o mapeamento abaixo.
- Não escreva lógica de negócio em controllers/endpoints — controllers só fazem mapping request → chamar service → format response.
- Use tipagem (type hints), docstrings mínimos e Pydantic para validação.

---

## Convenções globais

- Base do código: `src/robbot`
- Pacote raiz: `robbot` (lowercase)
- Imports absolutos: `from robbot.module.submodule import X`
- Nome de arquivos: `snake_case.py`, classes em `PascalCase`.
- Use f-strings para formatação.
- Linters/format: siga `black` / `flake8` conventions (80–100 cols OK).
- Tests: `pytest`, nomes `test_*.py`, fixtures quando necessário.

---

## Onde colocar cada tipo de código (mapeamento)

- **Entrypoint / app factory**
  - `src/robbot/main.py` — cria FastAPI app e registra routers (`api.v1.routers.api`)
- **Config**
  - `src/robbot/config/settings.py` — Pydantic `BaseSettings` (DATABASE_URL, SECRET_KEY, JWT settings)
- **Routers / Dependências**
  - `src/robbot/api/v1/routers/api.py` — inclui routers de feature (`include_router`)
  - `src/robbot/api/v1/dependencies.py` — `get_db()`, `get_current_user()`, OAuth2 scheme
- **Controllers (exposição HTTP — chamam Services)**
  - `src/robbot/adapters/controllers/*.py` — `auth_controller.py`, `users_controller.py`
- **Repositories (persistência, abstração do ORM)**
  - `src/robbot/adapters/repositories/*.py` — `user_repository.py` (métodos: `get_by_email`, `get_by_id`, `save`, `update`)
- **Domain (entidades / enums / DTOs)**
  - `src/robbot/domain/entities/*.py` — (domain objects, se usados)
  - `src/robbot/domain/enums.py` — enums de negócio (`Role`, `UserStatus`)
  - `src/robbot/domain/dtos/*.py` — DTOs internos se necessários
- **Services (regras de negócio / orquestração)**
  - `src/robbot/services/*.py` — `auth_service.py` (`signup`, `authenticate`, `create_tokens`, `refresh`, `revoke`)
- **Infra (ORM + models + migrations)**
  - `src/robbot/infra/db/base.py` — engine, `SessionLocal`, `Base`
  - `src/robbot/infra/db/models/*.py` — `user_model.py` (SQLAlchemy)
  - `alembic/` — migrações geradas; revisions em `alembic/versions`
- **Core (cross-cutting)**
  - `src/robbot/core/security.py` — hashing e JWT (create/access/verify/claims)
  - `src/robbot/core/exceptions.py` — exceptions customizadas
- **Schemas (Pydantic request/response)**
  - `src/robbot/schemas/user.py` — `UserCreate`, `UserOut`
  - `src/robbot/schemas/token.py` — `Token`, `TokenData`
- **Common (helpers compartilhados)**
  - `src/robbot/common/types.py` — tipos e enums utilitários
  - `src/robbot/common/utils.py` — helpers reutilizáveis
- **Tests**
  - `tests/unit/` — testes unitários por módulo (mocks)
  - `tests/integration/` — testes end-to-end (testcontainer ou DB de teste)

---

## Mapeamento concreto da feature `auth` (exemplo)

- **Entrypoint:** `src/robbot/main.py` — registra router: `app.include_router(api_router, prefix="/api/v1")`
- **Router:** `src/robbot/api/v1/routers/api.py` — `include_router(auth_controller.router, prefix="/auth")`
- **Controller HTTP:** `src/robbot/adapters/controllers/auth_controller.py` — endpoints `/token`, `/signup`
- **Service:** `src/robbot/services/auth_service.py` — `signup()`, `authenticate_user()`, `create_access_token()`
- **Repository:** `src/robbot/adapters/repositories/user_repository.py` — `get_by_email()`, `create_user()`
- **Model ORM:** `src/robbot/infra/db/models/user_model.py` — SQLAlchemy User table
- **Domain Enum:** `src/robbot/domain/enums.py` — `Role`, `UserStatus`
- **Core security:** `src/robbot/core/security.py` — `get_password_hash()`, `verify_password()`, `create_access_token()`, `decode_access_token()`
- **Schemas:** `src/robbot/schemas/user.py`, `src/robbot/schemas/token.py`
- **Dependency:** `src/robbot/api/v1/dependencies.py` — `OAuth2PasswordBearer`, `get_current_user()` que usa `core/security` + `user_repository`

---

## Regras “de ouro” de separação de responsabilidades

- **Controller:** NÃO acessar `engine`/`session` direto; receber dependências (`Depends`) e chamar Services.
- **Service:** contém lógica de negócio e orquestra repositórios e adaptadores; retorna DTOs / Model objects.
- **Repository:** só comunica com a DB (SQLAlchemy), encapsula queries e commits.
- **Core:** utilitários puros (sem acesso à DB).
- **Schemas:** Pydantic para inputs e outputs; use `orm_mode=True` em responses.

---

## Checklist automático (o LLM deve rodar antes de "entregar")

Para cada tarefa/PR gerada, verifique cada item abaixo; inclua resultado no final da entrega.

### A. Estrutura e local

- [ ] Arquivos foram colocados nos caminhos exatos conforme o mapeamento?
- [ ] Nomes dos arquivos respeitam `snake_case.py` e classes `PascalCase`?

### B. Código e responsabilidades

- [ ] Controllers não contêm lógica de negócio (apenas validação mínima + chamada a services)?
- [ ] Services chamam apenas repositories/adapters/core; não fazem queries SQL diretamente?
- [ ] Repositories usam `Session`/ORM e encapsulam commits/refresh?
- [ ] `core/security` não depende de DB?

### C. Qualidade e segurança

- [ ] Todas as funções públicas têm type hints e docstrings mínimos?
- [ ] Senhas não são armazenadas em texto; hashing com `passlib`/`bcrypt` é usado?
- [ ] `SECRET_KEY` e credenciais não estão hard-coded (apenas em `settings` e `.env`)?
- [ ] JWT usa algoritmo configurado em `settings` (`ALGORITHM`) e expira corretamente?

### D. Pydantic / Schemas / Enums

- [ ] Schemas de input vs output existem (ex.: `UserCreate` vs `UserOut`) e `response_model` é usado nos endpoints?
- [ ] Enums de domínio definidos em `domain/enums.py` e importados por models e schemas?

### E. Migrations e DB

- [ ] Se o model cria um enum nativo no Postgres, existe migration Alembic que cria o type antes da tabela?
- [ ] Não há `create_all()` em produção; migration Alembic está referenciada?

### F. Tests e CI

- [ ] Existem testes unitários para service principal (auth_service) com mocks de repositories?
- [ ] Existe pelo menos um teste de integração cover para `signup → login → /me` (opcionalmente com DB de teste)?
- [ ] Arquivos CI básicos (ex.: GitHub Actions) incluem execução de `pytest`?

### G. Estilo e entrega

- [ ] Código formatado por `black` (ou segue convenção)?
- [ ] Mensagem de commit segue padrão: `<area>: <descrição curta>` — ex.: `auth: add signup and token endpoints`
- [ ] PR description contém: resumo, links para issues (se houver), checklist de verificação (incluindo execução do checklist acima), instruções para testar localmente (docker compose / env)

---

## Checklist final (saída obrigatória)

Ao terminar, sempre inclua um bloco “Checklist result” mostrando cada item com `PASS` / `FAIL`. Em caso de `FAIL`, inclua instrução curta do que falta.

---

## Formato de entrega de arquivos

Quando gerar/alterar arquivos, retorne primeiro uma lista clara:

```
FILES CREATED:
- src/robbot/adapters/controllers/auth_controller.py — endpoint /auth/token, /auth/signup
- src/robbot/services/auth_service.py — lógica de signup/login
```

Em seguida, inclua cada arquivo em blocos com cabeçalho indicando `name=path`, por exemplo:

```text
name=src/robbot/adapters/controllers/auth_controller.py
<conteúdo do arquivo>
```

(Use o mesmo formato para cada arquivo.)

---

## Regras proibidas

- Não incluir segredos reais no código (`.env` ou valores secretos).
- Não executar `create_all()` em produção; se criar tabelas automaticamente, comente e documente que é apenas dev.

---

## Padrão de commits automatizados (integração do bloco)

Você também atuará como um engenheiro sênior de commits automatizados. Ao gerar/alterar arquivos localmente no repositório, siga este fluxo (quando for aplicável; se você não tiver acesso ao git, ainda gere a mensagem de commit sugerida):

### Fluxo esperado (pseudo-código para execução real pelo agente que fizer commits)

```bash
# 1. Obter arquivos modificados
arquivos=$(git status --porcelain | awk '{print $2}')

# 2. Loop para cada arquivo
for arquivo in $arquivos; do
    diff=$(git diff "$arquivo")
    # 3. Analisar o diff e gerar uma mensagem
    # Gere mensagem seguindo regras abaixo
    mensagem=<tipo>: <descrição curta (máx 60 chars)>
    git add "$arquivo"
    git commit -m "$mensagem"
done

# 4. Push final
git push
```

### Regras para gerar mensagens de commit

- Padrão: `tipo: descrição curta`
- Tipos possíveis: `feat`, `fix`, `docs`, `style`, `refactor`, `chore`
- Seja objetivo (máx 60 chars), verbos no presente (pt-BR: `adiciona`, `corrige`, `refatora`, `atualiza`).
- Baseie-se no diff para inferir o tipo; se incerto, use `chore`.
- Explique brevemente a decisão do tipo antes de executar os commits (para auditoria).
- Agrupe commits semelhantes quando fizer sentido, mantendo um único push no final.

Ao finalizar a geração de código, inclua:

- Mensagem de commit sugerida para cada arquivo/modificação.
- Um comando único `git push` sugerido para o conjunto de commits.

---

## Saída final exigida

Ao concluir a tarefa, o LLM deve retornar:

- Listagem dos arquivos criados/alterados (path + breve descrição).
- Conteúdo dos arquivos (blocos `name=path`).
- **CHECKLIST RESULT** (cada item `PASS` / `FAIL` com observações para `FAIL`).
- Como rodar local (ex.: copiar `.env`, `docker compose up --build`, `uvicorn ...`).
- Mensagens de commit sugeridas + PR title sugerido + PR body sugerido.

---

## O que foi feito

- Este documento padroniza o comportamento esperado do LLM ao gerar/editar código para o projeto `robbot`.

