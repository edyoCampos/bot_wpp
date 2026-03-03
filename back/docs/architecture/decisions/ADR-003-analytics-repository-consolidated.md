# ADR-002: Analytics Repository Consolidado em adapters/repositories

**Status:** ✅ Aceito e Implementado  
**Data:** 03/01/2026  
**Decisão Por:** Time de Desenvolvimento  
**Contexto:** Refatoração pós-auditoria técnica

---

## Contexto

O projeto tinha **dois diretórios de repositories** com padrões diferentes:

```
src/robbot/
├── adapters/repositories/        # 21 repositories ✅ PADRÃO CORRETO
│   ├── user_repository.py
│   ├── conversation_repository.py
│   └── ...
└── repositories/analytics/        # 1 repository ❌ FORA DO PADRÃO
    └── analytics_repository.py   (528 linhas - God Class)
```

Isso causava:
- **Confusão arquitetural**: Qual é o padrão? Onde criar novos repos?
- **Inconsistência**: `repositories` sem prefixo `adapters` sugere camada de domínio
- **Violação de Clean Architecture**: Repositories são **infraestrutura**, não domínio

---

## Decisão

**Consolidar TODOS os repositories em `adapters/repositories/`**:

```
src/robbot/adapters/repositories/
├── user_repository.py
├── conversation_repository.py
├── analytics/
│   └── analytics_repository.py  # Movido para cá
└── ... (21+ repositories)
```

**Deletar** a pasta `src/robbot/repositories/`.

---

## Consequências

### Positivas ✅

1. **Arquitetura Consistente**
   - Um único local para repositories
   - Novos desenvolvedores sabem onde criar repos

2. **Clean Architecture Correta**
   - `adapters/` = Infraestrutura (DB, HTTP, External APIs)
   - Repositories são **adapters** de persistência

3. **Imports Claros**
   ```python
   from robbot.adapters.repositories.analytics.analytics_repository import AnalyticsRepository
   # Caminho deixa claro que é infraestrutura
   ```

### Negativas ❌

1. **Refactor de Imports**
   - 2 arquivos precisaram ter imports atualizados
   - Overhead mínimo (feito automaticamente)

---

## God Class: analytics_repository.py (527 linhas)

### Problema Identificado

O `AnalyticsRepository` mistura **múltiplas responsabilidades**:
- Conversion analytics (150 linhas)
- Lead analytics (180 linhas)
- Performance analytics (150 linhas)
- User analytics (50 linhas)

### Decisão Futura (Não Crítico)

Quebrar em 4 repositories menores:
```
adapters/repositories/analytics/
├── analytics_conversion_repository.py  (150 linhas)
├── analytics_lead_repository.py        (180 linhas)
├── analytics_performance_repository.py (150 linhas)
└── analytics_user_repository.py        (50 linhas)
```

**Princípio:** Cada repository < 200 linhas, uma responsabilidade.

**Por que não foi feito agora?**
- Não é crítico para funcionamento
- Requer refactor de `MetricsService` que usa o repository
- Planejado para Sprint futuro

---

## Implementação

### Passos Executados

1. ✅ Criar `adapters/repositories/analytics/` directory
2. ✅ Mover `repositories/analytics/analytics_repository.py` → novo local
3. ✅ Atualizar imports em:
   - `services/analytics/metrics_service.py`
   - `adapters/controllers/dashboard_controller.py`
4. ✅ Deletar pasta `src/robbot/repositories/`
5. ✅ Validar código compila sem erros

### Arquivos Modificados

```python
# Antes
from robbot.repositories.analytics.analytics_repository import AnalyticsRepository

# Depois
from robbot.adapters.repositories.analytics.analytics_repository import AnalyticsRepository
```

---

## Alternativas Consideradas

### Alternativa 1: Manter duas pastas ❌
- **Decisão:** Rejeitado - Confusão permanente

### Alternativa 2: Mover analytics para `repositories/` ❌
- **Problema:** Viola Clean Architecture
- **Decisão:** Rejeitado

### Alternativa 3: Quebrar analytics_repository AGORA ❌
- **Problema:** Leva 2-3 horas adicionais
- **Decisão:** Adiado para sprint futuro (não crítico)

---

## Referências

- [Hexagonal Architecture - Ports & Adapters](https://alistair.cockburn.us/hexagonal-architecture/)
- [God Object Anti-Pattern](https://en.wikipedia.org/wiki/God_object)
- Auditoria Técnica 03/01/2026 - Problema Crítico #2

---

**Última Atualização:** 03/01/2026  
**Revisores:** Staff Engineer (Auditoria)  
**Status Quebra do God Class:** ⏭️ Planejado para futuro (não crítico)
