# ADR-001: Credential Separado de User

**Status:** ✅ Aceito e Implementado  
**Data:** 03/01/2026  
**Decisão Por:** Time de Desenvolvimento  
**Contexto:** Refatoração pós-auditoria técnica

---

## Contexto

Inicialmente, o `UserModel` continha o campo `hashed_password` junto com dados de domínio (email, nome, role), misturando **identidade do usuário** com **credenciais de segurança**.

```python
# Problema: Antes da refatoração
class UserModel(Base):
    email = Column(String(255))
    hashed_password = Column(String(255))  # ❌ Mistura domínio com auth
    full_name = Column(String(255))
    role = Column(String(50))
```

Isso violava o **Single Responsibility Principle (SRP)** e dificultava:
- Implementar autenticação via SSO/OAuth no futuro
- Trocar método de autenticação (senha → biometria, MFA)
- Queries rápidas de usuários sem carregar dados de autenticação

---

## Decisão

Criar **CredentialModel separado** com relationship 1:1 para User:

```python
# UserModel - Domínio puro
class UserModel(Base):
    email = Column(String(255))
    full_name = Column(String(255))
    role = Column(String(50))
    
    # Relationship
    credential = relationship("CredentialModel", uselist=False)

# CredentialModel - Segurança isolada
class CredentialModel(Base):
    user_id = Column(Integer, ForeignKey('users.id'))
    hashed_password = Column(String(255))
    mfa_secret = Column(String(255))
    backup_codes = Column(JSON)
    
    user = relationship("UserModel", back_populates="credential")
```

---

## Consequências

### Positivas ✅

1. **Separação de Responsabilidades (SRP)**
   - UserModel = Identidade e perfil
   - CredentialModel = Autenticação e segurança

2. **Futuro SSO/OAuth**
   - Possível adicionar `OAuthProviderModel` sem alterar UserModel
   - User pode ter múltiplas credenciais (senha + Google + GitHub)

3. **Performance**
   - Queries de listagem de usuários não carregam hashed_password
   - Índices menores em `users` table

4. **Segurança**
   - Credentials isoladas em tabela separada
   - Possível aplicar encryption at rest apenas em `credentials`
   - Auditoria focada em mudanças de senha

### Negativas ❌

1. **Join Necessário**
   - Autenticação requer `JOIN users ON credentials.user_id = users.id`
   - Overhead mínimo (índice em FK)

2. **Complexidade Inicial**
   - Mais um model para gerenciar
   - Migration de dados necessária

---

## Alternativas Consideradas

### Alternativa 1: Manter tudo em UserModel ❌
- **Prós:** Simplicidade inicial
- **Contras:** Violação SRP, impossível SSO, queries lentas
- **Decisão:** Rejeitado - dívida técnica

### Alternativa 2: AuthProvider abstrato ❌
- **Prós:** Suporta múltiplos providers desde o início
- **Contras:** Overengineering prematuro (não temos SSO ainda)
- **Decisão:** Rejeitado - YAGNI (You Aren't Gonna Need It)

---

## Implementação

### Migration Executada

1. **Criação de `credentials` table** (Migration `15a122075f87`)
2. **Migração de dados** `users.hashed_password` → `credentials.hashed_password`
3. **Remoção da coluna** (Migration `979ed2177922`)

### Código Atualizado

- ✅ `UserRepository` não recebe mais `hashed_password`
- ✅ `CredentialService` gerencia autenticação
- ✅ Todos os testes passando (12/12 auth + MFA)

---

## Referências

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)
- Auditoria Técnica 03/01/2026 - Problema Crítico #1

---

**Última Atualização:** 03/01/2026  
**Revisores:** Staff Engineer (Auditoria)
