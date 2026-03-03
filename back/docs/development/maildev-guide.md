# Guia Prático: Maildev em Desenvolvimento

## O que é Maildev?

**Maildev** é um servidor SMTP fake que **captura todos os emails** durante desenvolvimento, sem enviá-los para ninguém. Perfeito para:
- Testar fluxos de verificação de email
- Inspecionar conteúdo dos emails
- Desenvolver sem configurar Gmail/SendGrid
- Validar verificação de email em testes

## Acesso ao Maildev

### Web UI (Visualizar emails capturados)
```
http://localhost:1080
```

**O que você vê:**
- ✅ Lista de todos os emails capturados
- ✅ Conteúdo completo (HTML, texto)
- ✅ Headers (From, To, Subject)
- ✅ Links e attachments

### API REST (Programático)
```
http://localhost:1080/api
```

**Endpoints úteis:**
```bash
# GET todos os emails
curl http://localhost:1080/api/emails

# GET email específico por ID
curl http://localhost:1080/api/emails/{email_id}

# DELETE email
curl -X DELETE http://localhost:1080/api/emails/{email_id}

# DELETE todos os emails
curl -X DELETE http://localhost:1080/api/emails
```

## Configuração na API

### docker-compose.yml
```yaml
maildev:
  image: maildev/maildev:latest
  container_name: maildev
  restart: unless-stopped
  environment:
    - MAILDEV_WEB_PORT=1080      # Web UI port
    - MAILDEV_SMTP_PORT=1025     # SMTP port
  ports:
    - "127.0.0.1:1080:1080"      # Web access
    - "127.0.0.1:1025:1025"      # SMTP access
```

### Variáveis de Ambiente (.env)
```bash
# Em desenvolvimento (padrão)
SMTP_HOST=maildev
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_TLS=false

# SMTP_SENDER é opcional (padrão: no-reply@example.local)
SMTP_SENDER=no-reply@clinicago.local
```

## Fluxo de Email em Testes

### 1. Signup (cria user não verificado)
```python
requests.post(f"{api_url}/auth/signup", json={
    "email": "user@test.com",
    "password": "Test123!",
    ...
})
# ✅ Email de verificação enviado para Maildev
```

### 2. Capturar Email em Maildev
```python
# Poll Maildev API
response = requests.get("http://localhost:1080/api/emails")
emails = response.json()

# Procurar email para nosso usuário
for email in emails:
    if "user@test.com" in str(email):
        # Email encontrado!
```

### 3. Extrair Token de Verificação
```python
# Email contém link: http://localhost:3000/verify?token=xxx123
import re
match = re.search(r'token=([a-zA-Z0-9\-_.]+)', email_body)
verification_token = match.group(1)
```

### 4. Verificar Email (usar o token)
```python
requests.get(f"{api_url}/auth/verify-email", params={
    "token": verification_token
})
# ✅ Email agora verificado (email_verified=True)
```

### 5. Fazer Login
```python
response = requests.post(f"{api_url}/auth/token", data={
    "username": "user@test.com",
    "password": "Test123!"
})
access_token = response.json()["access_token"]
# ✅ Autenticado!
```

## Exemplo Completo (pytest fixture)

```python
def extract_verification_token(maildev_url: str, recipient_email: str) -> str:
    """Extrair token de verificação do email capturado no Maildev."""
    import re, time
    
    # Aguardar email (Maildev pode ter delay)
    for _ in range(20):  # 10 segundos de retry
        response = requests.get(f"{maildev_url}/api/emails")
        emails = response.json()
        
        for email in emails:
            to = str(email.get("to", []))
            if recipient_email in to:
                # Email encontrado - extrair token
                body = email.get("text", "")
                match = re.search(r'token=([a-zA-Z0-9\-_.]+)', body)
                if match:
                    return match.group(1)
        
        time.sleep(0.5)
    
    raise TimeoutError(f"Email não encontrado para {recipient_email}")

@pytest.fixture
def admin_token(api_url: str, maildev_url: str):
    email = "admin@test.com"
    password = "AdminTest123!"
    
    # 1. Signup
    requests.post(f"{api_url}/auth/signup", json={
        "email": email, "password": password, ...
    })
    
    # 2. Capturar token
    token = extract_verification_token(maildev_url, email)
    
    # 3. Verificar email
    requests.get(f"{api_url}/auth/verify-email", params={"token": token})
    
    # 4. Login
    resp = requests.post(f"{api_url}/auth/token", data={
        "username": email, "password": password
    })
    
    return resp.json()["access_token"]
```

## Troubleshooting

### ❌ "Email não aparece no Maildev"
**Causa:** API ainda não enviou ou Maildev não recebeu

**Solução:**
```bash
# 1. Verificar se Maildev está rodando
docker ps | grep maildev

# 2. Aumentar timeout na fixture (10s → 20s)
extract_verification_token(..., timeout=20)

# 3. Verificar logs da API
docker logs api | grep -i "email\|smtp"

# 4. Testar conectividade Maildev
curl http://localhost:1080/api/emails
```

### ❌ "SMTP connection refused"
**Causa:** Maildev não está rodando ou porta errada

**Solução:**
```bash
# Reiniciar containers
docker-compose restart maildev

# Verificar porta (deve ser 1025)
docker-compose ps maildev
```

### ❌ "Email enviado mas sem token no body"
**Causa:** Template de email não contém link de verificação

**Solução:**
- Verificar `EmailVerificationService.send_verification_email()`
- Confirmar que link é enviado com `?token=xxx`

## Limpeza

### Limpar todos os emails (entre testes)
```python
# Na fixture ou setup
requests.delete("http://localhost:1080/api/emails")
```

### Deletar email específico
```python
requests.delete("http://localhost:1080/api/emails/{email_id}")
```

## Best Practices em Testes

✅ **Sempre use timeout** ao aguardar emails
```python
token = extract_verification_token(maildev_url, email, timeout=10)
```

✅ **Limpar emails entre rodadas** para evitar ruído
```python
@pytest.fixture(autouse=True)
def cleanup_maildev(maildev_url):
    requests.delete(f"{maildev_url}/api/emails")
    yield
    requests.delete(f"{maildev_url}/api/emails")
```

✅ **Usar emails únicos** por teste
```python
email = f"test_{uuid.uuid4()}@example.com"
```

✅ **Lembrar que Maildev só roda localmente**
- Em CI/CD, pode ser necessário mock ou serviço real
- Ver `.github/workflows/tests.yml` para CI configuration

## Referências

- [Maildev GitHub](https://github.com/maildev/maildev)
- [Maildev API Docs](https://maildev.github.io/advanced-usage/api/)
- [Nossa implementação](../../../back/tests/api/conftest.py)
