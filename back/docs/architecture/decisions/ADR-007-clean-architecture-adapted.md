# ADR-004: Clean Architecture Adaptado (sem Domain Entities puras)

**Status:** ✅ Aceito e Implementado  
**Data:** 03/01/2026  
**Decisão Por:** Time de Desenvolvimento  
**Contexto:** Auditoria técnica revelou uso real de entities

---

## Contexto

### Auditoria Inicial (Incorreta)

A auditoria inicial de 03/01/2026 identificou que **domain entities não eram usadas**:

```bash
$ grep -r "from robbot.domain.entities import" src/
# Resultado esperado: 0 matches
```

Isso levou à recomendação de **deletar** domain/entities.

### Validação Posterior (Correção)

Ao tentar deletar, descobrimos que **entities SÃO usadas** em:
- 10 services (conversation_orchestrator, playbook_service, lead_service, etc.)
- 7 repositories (audit_log_repository, lead_repository, etc.)
- Total: **20+ imports ativos**

**Conclusão:** Auditoria estava incorreta. Entities existem E são utilizadas.

---

## Decisão

**Manter domain/entities/** mas adaptar Clean Architecture ao contexto do projeto:

### Camadas Implementadas

```
src/robbot/
├── domain/              # Domínio puro
│   ├── entities/        # Dataclasses sem lógica de infra
│   │   ├── lead.py
│   │   ├── conversation.py
│   │   └── ... (10 entities)
│   └── enums.py         # Enums de negócio
├── adapters/            # Infraestrutura
│   ├── controllers/     # REST endpoints (FastAPI)
│   ├── repositories/    # Persistência (SQLAlchemy)
│   └── external/        # Clients HTTP (Gemini, WAHA)
├── infra/               # Implementações técnicas
│   ├── db/models/       # ORM Models (SQLAlchemy)
│   ├── jobs/            # Workers (RQ)
│   ├── redis/           # Cache
│   └── vectordb/        # ChromaDB
├── services/            # Lógica de negócio
├── schemas/             # DTOs Pydantic (API)
└── core/                # Utilities (exceptions, security, logging)
```

### Uso de Entities vs Models

**Entities (Domain):**
- Dataclasses puros sem dependência de infra
- Usados em **lógica de negócio** (services)
- Exemplo: `Lead`, `Conversation`, `PlaybookStep`

**Models (Infra):**
- SQLAlchemy ORM classes
- Mapeamento direto para banco de dados
- Usados em **repositories**

**Schemas (API):**
- Pydantic models para validação
- Request/Response de endpoints

---

## Consequências

### Positivas ✅

1. **Separação de Domínio e Infra**
   - Entities não dependem de SQLAlchemy
   - Possível testar lógica de negócio sem banco

2. **Flexibilidade**
   - Trocar ORM (SQLAlchemy → Tortoise) sem alterar entities
   - Adicionar MongoDB para alguns models sem afetar domínio

3. **Clareza de Responsabilidades**
   - Entities = **O QUE** (domínio)
   - Models = **COMO** (persistência)
   - Schemas = **INTERFACE** (API)

### Negativas ❌

1. **Duplicação Aparente**
   - `Lead` existe como Entity, Model E Schema
   - Justificativa: Responsabilidades diferentes

2. **Conversão Necessária**
   - Repository converte Model → Entity
   - Service recebe Entity, retorna Entity
   - Controller converte Entity → Schema

3. **Curva de Aprendizado**
   - Novos devs precisam entender 3 representações

---

## Padrão de Conversão

### Repository → Service (Model → Entity)

```python
# LeadRepository
def get_by_id(self, lead_id: str) -> Lead:  # Retorna Entity
    model = self.db.query(LeadModel).get(lead_id)
    
    # Conversão Model → Entity
    return Lead(
        id=model.id,
        name=model.name,
        phone_number=model.phone_number,
        status=model.status,
        maturity_score=model.maturity_score,
        # ... outros campos
    )
```

### Service → Controller (Entity → Schema)

```python
# LeadService
def create_lead(self, data: dict) -> Lead:  # Recebe dict, retorna Entity
    entity = Lead(**data)
    # Lógica de negócio aqui
    return self.repo.create(entity)

# LeadController
@router.post("/leads")
def create_lead_endpoint(data: LeadCreate) -> LeadResponse:  # Schemas Pydantic
    entity = service.create_lead(data.dict())
    
    # Conversão Entity → Schema
    return LeadResponse(
        id=entity.id,
        name=entity.name,
        # ... outros campos
    )
```

---

## Por que NÃO deletar domain/entities?

### Razão 1: Uso Extensivo no Código

20+ arquivos importam entities:
```python
from robbot.domain.entities.lead import Lead
from robbot.domain.entities.conversation import Conversation
from robbot.domain.entities.playbook import Playbook
# ... etc
```

Deletar quebraria o sistema inteiro.

### Razão 2: Lógica de Domínio Rica (Futuro)

Entities podem ter métodos de domínio:

```python
@dataclass
class Lead:
    maturity_score: int
    
    def is_qualified(self) -> bool:
        """Regra de negócio: Lead qualificado se score >= 70"""
        return self.maturity_score >= 70
    
    def can_convert(self) -> bool:
        """Lead pode ser convertido se qualificado e status adequado"""
        return self.is_qualified() and self.status in [LeadStatus.PROPOSAL, LeadStatus.NEGOTIATION]
```

Essa lógica **não deveria** estar em `LeadModel` (ORM) nem em `LeadService`.

### Razão 3: Testabilidade

```python
# Teste de domínio SEM banco de dados
def test_lead_qualification():
    lead = Lead(maturity_score=80, status=LeadStatus.PROPOSAL)
    assert lead.is_qualified() == True
    assert lead.can_convert() == True
```

Usar Models requereria setup de SQLAlchemy + DB.

---

## Quando Usar Cada Camada

| Tipo | Onde Usar | Exemplo |
|------|-----------|---------|
| **Entity** | Services, lógica de negócio | `Lead`, `Conversation` |
| **Model** | Repositories, queries SQL | `LeadModel`, `ConversationModel` |
| **Schema** | Controllers, validação API | `LeadCreate`, `LeadResponse` |

---

## Alternativas Consideradas

### Alternativa 1: Usar apenas Models (ORM direto) ❌

```python
# Service recebe/retorna SQLAlchemy models
def create_lead(self, data: dict) -> LeadModel:
    model = LeadModel(**data)
    self.db.add(model)
    return model
```

**Problemas:**
- Service acoplado ao ORM
- Impossível testar sem banco
- Trocar ORM quebra todos os services

**Decisão:** Rejeitado

### Alternativa 2: Domain Entities com lógica rica ⚠️

```python
@dataclass
class Lead:
    def save(self):  # ❌ Entity salvando no banco
        repository.save(self)
```

**Problema:** Entity não deveria conhecer infraestrutura

**Decisão:** Rejeitado - Entities são **puros** (sem I/O)

### Alternativa 3: Usar Schemas como Entities ❌

```python
# Pydantic models em services
def create_lead(self, data: LeadCreate) -> LeadResponse:
    # Lógica com Pydantic
```

**Problema:** Pydantic é para validação de API, não domínio

**Decisão:** Rejeitado - Mistura responsabilidades

---

## Referências

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [DDD: Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- Auditoria Técnica 03/01/2026 - Problema #3 (corrigido)

---

**Última Atualização:** 03/01/2026  
**Status Entities:** ✅ Mantidas e em uso ativo  
**Imports Ativos:** 20+ arquivos
