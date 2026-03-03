<div align="center">

# 🤖 GO ROBOT - Backend

**Sistema backend para chatbot WhatsApp com FastAPI, PostgreSQL, Redis e serviços auxiliares**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![uv](https://img.shields.io/badge/uv-package%20manager-orange.svg)](https://docs.astral.sh/uv/)

</div>

---

## 📋 Índice

- [Pré-requisitos](#-pré-requisitos)
- [Instalação do uv](#-instalação-do-uv)
- [Clonando o Projeto](#-clonando-o-projeto)
- [Configuração Inicial](#-configuração-inicial)
- [Docker - Guia Completo](#-docker---guia-completo)
- [Auto Commit](#-auto-commit)
- [Rotina Diária](#-rotina-diária)
- [Desenvolvimento Local](#-desenvolvimento-local)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Pré-requisitos

<table>
<tr>
<td width="50%">

### 🖥️ Ferramentas Essenciais

- ✅ [Docker Desktop](https://www.docker.com/products/docker-desktop/) ou Docker Engine
- ✅ [Git](https://git-scm.com/downloads)
- ✅ [Python 3.11+](https://www.python.org/downloads/)
- ✅ [uv](https://docs.astral.sh/uv/) (instalação abaixo)

</td>
<td width="50%">

### 💻 Terminal Recomendado

- **Windows**: PowerShell ou Git Bash
- **Linux/Mac**: Terminal padrão (bash/zsh)

> 💡 **Dica**: Escolha um terminal e use-o consistentemente

</td>
</tr>
</table>

---

## 📦 Instalação do uv

> **uv** é o gerenciador de pacotes Python ultrarrápido usado neste projeto. Ele substitui pip/poetry/conda.

<details open>
<summary><b>🪟 Windows (PowerShell)</b></summary>

### 1️⃣ Instalar o uv

Execute no **PowerShell** como usuário normal (não precisa de admin):

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2️⃣ Recarregar o Terminal

**IMPORTANTE**: Após a instalação, **feche e abra novamente o PowerShell** para que o comando `uv` seja reconhecido.

### 3️⃣ Verificar a Instalação

```powershell
# Verificar versão
uv --version

# Se der erro "comando não encontrado", verifique o PATH:
$env:PATH -split ';' | Select-String -Pattern "uv"
```

### ⚠️ Troubleshooting

<details>
<summary>Se <code>uv --version</code> não funcionar...</summary>

```powershell
# 1. Verifique se o executável existe
Test-Path "$env:USERPROFILE\.cargo\bin\uv.exe"

# 2. Se existir mas não funcionar, adicione ao PATH:

# Opção A: Adicionar PERMANENTEMENTE via PowerShell (recomendado) ⭐
[Environment]::SetEnvironmentVariable(
    "Path",
    "$env:USERPROFILE\.cargo\bin;$([Environment]::GetEnvironmentVariable('Path', 'User'))",
    "User"
)

# Opção B: Adicionar TEMPORARIAMENTE (só para a sessão atual)
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"

# Opção C: Via GUI do Windows
# Painel de Controle → Sistema → Configurações avançadas → Variáveis de Ambiente
# Adicione: %USERPROFILE%\.cargo\bin ao PATH do usuário

# 3. IMPORTANTE: Feche e abra novamente o PowerShell

# 4. Teste novamente
uv --version
```

</details>

</details>

<details>
<summary><b>🐧 Linux / WSL / 🍎 macOS</b></summary>

### 1️⃣ Instalar o uv

Execute no **bash/zsh**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Recarregar o Shell

**IMPORTANTE**: O script adiciona `uv` ao `~/.local/bin`, mas você precisa recarregar o shell:

<table>
<tr>
<td width="50%">

**Opção A: Reiniciar Terminal** ⭐

```bash
# Feche e abra novamente o terminal
# (Forma mais confiável)
```

</td>
<td width="50%">

**Opção B: Recarregar Profile**

```bash
# Para bash:
source ~/.bashrc

# Para zsh:
source ~/.zshrc
```

</td>
</tr>
</table>

### 3️⃣ Verificar a Instalação

```bash
# Verificar versão
uv --version

# Verificar se ~/.local/bin está no PATH
echo $PATH | grep -i ".local/bin"
# ✅ Deve mostrar o caminho incluindo ~/.local/bin
```

### ⚠️ Troubleshooting

<details>
<summary>Se <code>uv --version</code> não funcionar...</summary>

```bash
# 1. Verificar se o executável existe
ls -la ~/.local/bin/uv

# 2. Verificar se ~/.local/bin está no PATH
echo $PATH | grep ".local/bin"

# 3. Se NÃO estiver no PATH, adicione manualmente:

# Para bash:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Para zsh:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 4. Teste novamente
uv --version
```

</details>

</details>

<div align="center">

✅ **Instalação concluída!** Prossiga para clonar o projeto.

</div>

---

## 📥 Clonando o Projeto

<details open>
<summary><b>🎥 Tutorial Visual Disponível</b></summary>

📹 [Assista ao tutorial completo no Notion](https://www.notion.so/Git-Clone-2984d53b3ec280b78d9ef14bf76cc3a3?source=copy_link)

</details>

### Passo a Passo

<table>
<tr>
<td width="50%">

#### Para Git Bash

```bash
# 1. Verificar se o diretório está vazio
ls -la

# 2. (Se necessário) Limpar diretório ⚠️
rm -rf * .* 2>/dev/null || true

# 3. Clonar o repositório
git clone https://github.com/FAQ-com-chatbot-WhatsApp/faqchatbot.git .

# 4. Ajustar para Windows (NTFS)
git config core.protectNTFS false

# 5. Atualizar branches
git checkout main
git pull origin main

# (Opcional) Branch grupotic
git checkout grupotic
git pull origin grupotic

# 6. Verificar resultado
git branch -a
```

</td>
<td width="50%">

#### Para PowerShell

```powershell
# 1. Verificar se o diretório está vazio
Get-ChildItem -Force

# 2. (Se necessário) Limpar diretório ⚠️
Remove-Item * -Recurse -Force

# 3. Clonar o repositório
git clone https://github.com/FAQ-com-chatbot-WhatsApp/faqchatbot.git .

# 4. Ajustar para Windows (NTFS)
git config core.protectNTFS false

# 5. Atualizar branches
git checkout main
git pull origin main

# (Opcional) Branch grupotic
git checkout grupotic
git pull origin grupotic

# 6. Verificar resultado
git branch -a
```

</td>
</tr>
</table>

---

## ⚙️ Configuração Inicial

### 1️⃣ Preparar Arquivo de Ambiente (.env)

O projeto utiliza um arquivo `.env` para gerenciar segredos e configurações.

1.  **Navegue até a pasta `back`**:
    ```bash
    cd <seu-diretorio>/clinica_go/back
    ```

2.  **Copie o arquivo de exemplo**:
    ```bash
    # No Git Bash
    cp .env.example .env

    # No PowerShell
    Copy-Item .env.example .env
    ```

3.  **Preencha as variáveis obrigatórias** no arquivo `.env` recém-criado:
    -   `SECRET_KEY`: Gere uma chave segura. Você pode usar o comando `openssl rand -hex 32` no Git Bash ou um gerador online.
    -   `GOOGLE_API_KEY`: Obtenha sua chave de API no [Google AI Studio](https://ai.google.dev/).

### 2️⃣ Obter Credenciais da API do WhatsApp (WAHA)

O serviço `waha` precisa de credenciais que são geradas na primeira vez que ele é executado. Siga estes passos **exatamente**.

1.  **Verifique o `.env`**: Certifique-se de que as seguintes variáveis estejam **vazias** no seu arquivo `.env`:
    ```dotenv
    WAHA_API_KEY=
    WAHA_DASHBOARD_USERNAME=
    WAHA_DASHBOARD_PASSWORD=
    WHATSAPP_SWAGGER_USERNAME=
    WHATSAPP_SWAGGER_PASSWORD=
    ```

2.  **Inicie apenas o serviço `waha`**:
    ```bash
    # Certifique-se de estar na pasta 'back/'
    docker compose up -d waha
    ```

3.  **Capture as credenciais geradas**: Verifique os logs do `waha` para encontrar as chaves geradas.
    ```bash
    docker compose logs waha
    ```
    Você verá uma saída parecida com esta:
    ```
    ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️
    Generated credentials (persist to .env or WAHA_* env vars)
    Save these values to your environment (.env or WAHA_*) to reuse them; new keys are generated on every start otherwise.

    cat <<'EOF' > .env

    WAHA_API_KEY=3d05309716bd4dbcbb87102778f050d7
    WAHA_DASHBOARD_PASSWORD=50a84a5765484c5c9ab805d6bc470e33
    WHATSAPP_SWAGGER_PASSWORD=50a84a5765484c5c9ab805d6bc470e33
    EOF

    Generated credentials ready to copy
    ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️
    ```

4.  **Atualize o `.env`**: Copie os valores gerados (`WAHA_API_KEY`, `WAHA_DASHBOARD_PASSWORD`, etc.) para o seu arquivo `.env`. Para os usernames, você pode usar `admin`.
    ```dotenv
    WAHA_API_KEY=3d05309716bd4dbcbb87102778f050d7
    WAHA_DASHBOARD_USERNAME=admin
    WAHA_DASHBOARD_PASSWORD=50a84a5765484c5c9ab805d6bc470e33
    WHATSAPP_SWAGGER_USERNAME=admin
    WHATSAPP_SWAGGER_PASSWORD=50a84a5765484c5c9ab805d6bc470e33
    ```

5.  **Pare o serviço `waha`** antes de prosseguir:
    ```bash
    docker compose stop waha
    ```

### 3️⃣ Preparar Auto Commit

<table>
<tr>
<td width="50%">

**Git Bash**

```bash
# Navegar para a RAIZ do projeto (onde está o .git)
cd <seu-diretorio>/clinica_go

# O script auto-commit.sh já está aqui e tem permissão de execução
# Verifique: ls -la | grep auto-commit
```

</td>
<td width="50%">

**PowerShell**

```powershell
# Liberar execução de scripts (primeira vez)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Navegar para a RAIZ do projeto (onde está o .git)
cd <seu-diretorio>\clinica_go

# O script auto-commit.ps1 já está aqui
# Verifique: Get-ChildItem -Filter auto-commit.*
```

</td>
</tr>
</table>

### 2️⃣ Configurar Ambiente Python

<table>
<tr>
<td width="50%">

**Git Bash**

```bash
# Navegar para a pasta back (onde está o pyproject.toml)
cd <seu-diretorio>/clinica_go/back

# Criar ambiente e instalar dependências
uv sync

# Ativar ambiente
source .venv/Scripts/activate
```

</td>
<td width="50%">

**PowerShell**

```powershell
# Navegar para a pasta back (onde está o pyproject.toml)
cd <seu-diretorio>\clinica_go\back

# Criar ambiente e instalar dependências
uv sync

# Ativar ambiente
.\.venv\Scripts\Activate.ps1
```

</td>
</tr>
</table>

> 💡 **Dica**: `uv sync` lê automaticamente o `pyproject.toml`, cria o ambiente virtual e instala todas as dependências necessárias em um único comando.

---

## 🐳 Docker - Guia Completo

### 📂 Estrutura

```
clinica_go/                   ← RAIZ (execute auto-commit aqui)
├── .git/
├── auto-commit.ps1
├── auto-commit.sh
└── back/                     ← BACK (execute docker/uv aqui)
    ├── docker-compose.yml
    ├── Dockerfile
    ├── Dockerfile.worker
    ├── pyproject.toml
    ├── .venv/
    └── src/
        └── robbot/           ← Código fonte
```

> ⚠️ **Importante**: Comandos **docker** e **uv** devem ser executados de dentro da pasta **`back/`**

### 🚀 Comandos Principais

<details open>
<summary><b>Iniciar Serviços</b></summary>

```bash
# Subir todos os serviços em background
docker compose up -d

# Subir com 2 workers (recomendado)
docker compose up -d --scale worker=2

# Verificar status
docker compose ps

# Ver logs em tempo real
docker compose logs -f
```

</details>

<details>
<summary><b>Parar Serviços</b></summary>

```bash
# Opção A: Parar e remover containers (recomendado)
docker compose down

# Opção B: Apenas parar (mantém containers)
docker compose stop
```

</details>

<details>
<summary><b>Retomar Serviços</b></summary>

```bash
# Se usou 'stop' → use 'start' (mais rápido)
docker compose start

# Se usou 'down' → use 'up -d' (recria containers)
docker compose up -d --scale worker=2
```

</details>

<details>
<summary><b>Reconstruir Imagens</b></summary>

```bash
# Reconstruir do zero (sem cache)
docker compose build --no-cache

# Subir com as novas imagens
docker compose up -d --scale worker=2
```

</details>

### 🌐 URLs dos Serviços

| 🔗 Serviço  | URL                        | Descrição                         |
| ----------- | -------------------------- | --------------------------------- |
| 🚀 API      | http://localhost:3333      | API FastAPI principal             |
| 📚 API Docs | http://localhost:3333/docs | Documentação interativa (Swagger) |
| 🗄️ Adminer  | http://localhost:8080      | Interface web do PostgreSQL       |
| 💬 WhatsApp | http://localhost:3000      | Servidor WAHA                     |

### 📊 Tabela de Comandos Docker

| Comando             | Função                       | Quando usar                 |
| ------------------- | ---------------------------- | --------------------------- |
| `up -d`             | Cria e inicia containers     | Primeira vez ou após `down` |
| `start`             | Inicia containers parados    | Após usar `stop`            |
| `stop`              | Para containers (não remove) | Pausar sem remover dados    |
| `down`              | Para e remove containers     | Encerrar o dia              |
| `down -v`           | Remove containers + volumes  | Limpar banco de dados       |
| `logs -f`           | Ver logs em tempo real       | Debugging                   |
| `restart <serviço>` | Reinicia um serviço          | Recarregar código           |
| `ps`                | Lista containers ativos      | Verificar status            |

### 🔧 Comandos Úteis

```bash
# Ver logs de um serviço específico
docker compose logs -f api

# Ver logs dos workers
docker compose logs -f worker

# Reiniciar apenas um serviço
docker compose restart api

# Executar comando dentro do container
docker exec -it api bash

# Limpar tudo (containers, volumes, imagens não usadas)
docker system prune -a --volumes
```

---

## 🤖 Auto Commit

> Sistema automatizado de commits seguindo [Conventional Commits](https://www.conventionalcommits.org/)

> ⚠️ **IMPORTANTE**: Execute o auto-commit **DA RAIZ DO PROJETO** (onde está o `.git`), NÃO da pasta `back/`!

### Como Funciona

1. 🔍 Analisa mudanças no repositório
2. 🏷️ Classifica automaticamente o tipo de commit
3. 📦 Agrupa commits similares (docs, style, tests)
4. ✍️ Cria commits individuais para features/fixes
5. 🚀 Push único de todos os commits

### Tipos de Commit Automáticos

| Tipo       | Exemplo                            | Quando Aplica                  |
| ---------- | ---------------------------------- | ------------------------------ |
| `feat`     | `feat: adiciona user_service.py`   | Novos arquivos/funcionalidades |
| `fix`      | `fix: corrige lógica em auth.py`   | Correções de bugs              |
| `docs`     | `docs: atualiza documentação`      | Arquivos .md, README           |
| `style`    | `style: ajusta formatação`         | Mudanças de formatação         |
| `refactor` | `refactor: refatora user_model.py` | Refatorações                   |
| `chore`    | `chore: atualiza configuração`     | Config, deps, testes           |

### Uso Seguro

<table>
<tr>
<td width="50%">

#### Git Bash

```bash
# 1. Revisar mudanças
git status
git diff

# 2. Executar o script (DA RAIZ do projeto, não de back/)
cd ..
./auto-commit.sh

# Durante execução:
# ⏱️ Aguarda 5s → Ctrl+C para abortar
# ⏱️ Aguarda 3s antes do push → Ctrl+C para evitar
```

</td>
<td width="50%">

#### PowerShell

```powershell
# 1. Liberar execução (primeira vez)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 2. Revisar mudanças
git status
git diff

# 3. Executar o script (DA RAIZ do projeto, não de back/)
cd ..
.\auto-commit.ps1

# Durante execução:
# ⏱️ Aguarda 5s → Ctrl+C para abortar
# ⏱️ Aguarda 3s antes do push → Ctrl+C para evitar
```

</td>
</tr>
</table>

### ✅ Checklist Antes de Executar

- [ ] Revisei todas as mudanças com `git diff`
- [ ] Não há arquivos sensíveis (.env, tokens, senhas)
- [ ] Estou na branch correta (`git branch`)
- [ ] .gitignore está configurado corretamente
- [ ] Li o plano de commits que o script apresentará

### ⚠️ Cuidados Importantes

> 🚨 **NUNCA commite arquivos sensíveis**: `.env`, tokens, senhas, chaves de API

- Use `git status` antes de executar
- Revise o plano de commits durante os 5s de espera
- Use `Ctrl+C` se algo estiver errado
- Mantenha o .gitignore atualizado
- Scripts detectam automaticamente arquivos deletados, renomeados e modificados

### 🔄 Reverter Commits (Se Necessário)

```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer últimos 3 commits
git reset --soft HEAD~3

# Forçar push (⚠️ use com cuidado em branches compartilhadas)
git push origin nome-da-branch --force
```

---

## 📅 Rotina Diária

### 🌅 Começando o Dia

```bash
# 1. Atualizar repositório (DA RAIZ do projeto)
cd D:/_projects/clinica_go  # ou seu caminho
git checkout main
git pull origin main
git checkout sua-branch
git merge main  # ou git rebase main

# 2. Ir para a pasta back e subir Docker
cd back
docker compose up -d --scale worker=2
sleep 5
docker compose ps

# 3. Ativar ambiente Python (já em back/)
source .venv/Scripts/activate  # Git Bash
# .\.venv\Scripts\Activate.ps1  # PowerShell

# 4. Ver logs
docker compose logs -f api
docker compose logs -f worker  # Logs dos workers
```

### 💼 Durante o Dia

```bash
# Ver status dos containers (executar de back/)
cd D:/_projects/clinica_go/back
docker compose ps

# Logs de um serviço
docker compose logs -f api

# Logs dos workers
docker compose logs -f worker

# Reiniciar serviço após mudanças
docker compose restart api

# Verificar mudanças Git (executar da RAIZ)
cd ..
git status
git diff
```

### 🌙 Encerrando o Dia

```bash
# 1. Voltar para a RAIZ e commitar mudanças
cd D:/_projects/clinica_go  # ou seu caminho
./auto-commit.sh  # Git Bash
# .\auto-commit.ps1  # PowerShell

# 2. Ir para back/ e parar Docker
cd back
docker compose down

# 3. Desativar ambiente Python
deactivate
```

### 🔄 Workflow Git Diário

```bash
# Salvar trabalho temporário
git stash

# Atualizar main
git checkout main
git pull origin main

# Voltar para sua branch
git checkout minha-feature

# Opção A: Merge (simples)
git merge main

# OU Opção B: Rebase (histórico linear)
git rebase main

# Restaurar trabalho
git stash pop
```

---

## 💻 Desenvolvimento Local

### Executar Aplicação sem Docker

```bash
# 1. Navegar para a pasta back e ativar ambiente
cd D:/_projects/clinica_go/back  # ou seu caminho
source .venv/Scripts/activate  # Git Bash
# .\.venv\Scripts\Activate.ps1  # PowerShell

# 2. Executar migrações
alembic upgrade head

# 3. Rodar aplicação
uvicorn robbot.main:app --reload --host 0.0.0.0 --port 3333
```

### Gerenciar Dependências com uv

```bash
# Adicionar nova dependência
uv add nome-do-pacote

# Adicionar dependência de desenvolvimento
uv add --dev nome-do-pacote

# Remover dependência
uv remove nome-do-pacote

# Atualizar dependências
uv sync --upgrade

# Listar pacotes instalados
uv pip list
```

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/
pytest tests/integration/

# Com cobertura
pytest --cov=robbot
```

---

## 🔧 Troubleshooting

<details>
<summary><b>❌ Erro: "no configuration file provided"</b></summary>

**Problema**: Comando docker-compose não funciona.

**Solução**:

```bash
# ❌ Antigo (Docker Compose V1)
docker-compose down

# ✅ Novo (Docker Compose V2 - recomendado)
docker compose down
```

</details>

<details>
<summary><b>❌ Erro: "port is already allocated"</b></summary>

**Problema**: Porta já está em uso por outro processo.

**Solução**:

```bash
# Ver processos usando a porta
netstat -ano | findstr :3333  # Windows
lsof -i :3333                 # Linux/Mac

# Parar todos os containers
docker compose down
```

</details>

<details>
<summary><b>❌ Container não inicia / fica reiniciando</b></summary>

**Solução**:

```bash
# Ver logs detalhados
docker compose logs api

# Verificar saúde do container
docker inspect api

# Reconstruir sem cache
docker compose build --no-cache api
docker compose up -d --scale worker=2
```

</details>

<details>
<summary><b>❌ Erro: "permission denied" ao executar auto-commit.sh</b></summary>

**Solução**:

```bash
# Navegue para a RAIZ do projeto primeiro
cd D:/_projects/clinica_go  # ou seu caminho

# Dê permissão de execução
chmod +x auto-commit.sh
```

</details>

<details>
<summary><b>❌ PowerShell: "cannot be loaded because running scripts is disabled"</b></summary>

**Solução**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

</details>

<details>
<summary><b>❌ uv: "command not found"</b></summary>

**Solução**: Reinstale o uv seguindo as [instruções de instalação](#-instalação-do-uv)

Depois, reinicie o terminal.

</details>

---

## 📚 Recursos Adicionais

- 📖 [Documentação FastAPI](https://fastapi.tiangolo.com/)
- 🐳 [Docker Compose Docs](https://docs.docker.com/compose/)
- 📦 [uv Documentation](https://docs.astral.sh/uv/)
- 🔀 [Conventional Commits](https://www.conventionalcommits.org/)
- 🎨 [Git Best Practices](https://git-scm.com/book/en/v2)

---

## 🆘 Suporte

<div align="center">

**Precisa de ajuda?**

1. 📋 Verifique os logs: `docker-compose -f docker/docker-compose.yml logs`
2. 📖 Revise este README
3. 💬 Contate o time de desenvolvimento

---

<sub>Feito com ❤️ pela equipe FAQ Chatbot WhatsApp</sub>

</div>
