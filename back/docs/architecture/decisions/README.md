# Architecture Decision Records (ADRs)

Este diretorio contem as decisoes arquiteturais importantes do projeto **Clinica Go Backend**.

ADRs documentam o **contexto**, **decisao**, **consequencias** e **alternativas** de escolhas tecnicas relevantes.

---

## Indice de ADRs

### Implementados

| ADR | Titulo | Data | Status |
|-----|--------|------|--------|
| [ADR-001](ADR-001-credential-separated-from-user.md) | Credential Separado de User | 03/01/2026 | Aceito |
| [ADR-002](ADR-002-dependency-injection-pattern.md) | Dependency Injection Pattern | 04/01/2026 | Aceito |
| [ADR-003](ADR-003-analytics-repository-consolidated.md) | Analytics Repository Consolidado | 03/01/2026 | Aceito |
| [ADR-004](ADR-004-repository-interface-pattern.md) | Repository Interface Pattern | 04/01/2026 | Aceito |
| [ADR-005](ADR-005-custom-exceptions-hierarchy.md) | Custom Exceptions com Hierarquia | 30/12/2025 | Aceito |
| [ADR-006](ADR-006-session-dependency-injection.md) | Session Dependency Injection | 04/01/2026 | Aceito |
| [ADR-007](ADR-007-clean-architecture-adapted.md) | Clean Architecture Adaptado | 03/01/2026 | Aceito |
| [ADR-008](ADR-008-service-decomposition-strategy.md) | Service Decomposition Strategy | 05/01/2026 | Aceito |
| [ADR-009](ADR-009-major-technical-refactoring-2026-01.md) | Major Technical Refactoring | 13/01/2026 | Aceito |
| [ADR-010](ADR-010-analytics-repository-consolidation.md) | Analytics Repository Consolidation | 18/01/2026 | Aceito |
---

## Template para Novos ADRs

Ao criar um novo ADR, use o seguinte template:

```markdown
# ADR-XXX: [Titulo da Decisao]

**Status:** [Proposto | Aceito | Rejeitado | Substituido | Obsoleto] 
**Data:** DD/MM/YYYY 
**Decisao Por:** [Time/Pessoa] 
**Contexto:** [Situacao que motivou a decisao]

---

## Contexto

[Descricao do problema ou necessidade que levou a decisao]

---

## Decisao

[Descricao clara da decisao tomada]

---

## Consequencias

### Positivas 
[Lista de beneficios]

### Negativas 
[Lista de trade-offs ou custos]

---

## Alternativas Consideradas

### Alternativa 1: [Nome] 
- **Pros:** ...
- **Contras:** ...
- **Decisao:** Rejeitado porque...

---

## Implementacao

[Como a decisao foi implementada, se aplicavel]

---

## Referencias

[Links, artigos, documentacoes relevantes]

---

**Ultima Atualizacao:** DD/MM/YYYY
```

---

## Proximos ADRs Planejados

- **ADR-011:** Estrategia de Cache (Redis)
- **ADR-012:** Vector Database para RAG (ChromaDB)
- **ADR-013:** Background Jobs com RQ
- **ADR-014:** Autenticacao MFA (TOTP)
- **ADR-015:** Rate Limiting Strategy
- **ADR-016:** WebSocket para Real-time Updates

---

## Boas Praticas

### Quando Criar um ADR?

Crie um ADR quando:
- A decisao tem **impacto significativo** na arquitetura
- A decisao e **dificil de reverter** (migracao complexa)
- Ha **multiplas alternativas** razoaveis
- A decisao pode gerar **duvidas futuras** ("por que fizemos assim?")

### Quando NAO Criar um ADR?

Nao crie para:
- Decisoes triviais ou padrao da linguagem
- Escolhas temporarias ou experimentais
- Detalhes de implementacao sem impacto arquitetural

### Manutencao

- **Revisar ADRs** ao menos 1x por trimestre
- **Atualizar status** se decisao foi revertida ou substituida
- **Referenciar ADRs** em Pull Requests de mudancas arquiteturais

---

**Ultima Atualizacao:** 03/01/2026 
**Total de ADRs:** 4
