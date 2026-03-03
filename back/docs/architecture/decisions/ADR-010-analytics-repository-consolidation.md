# ADR-007: Consolidação de Repositórios de Analytics

**Status:** ✅ Aceito  
**Data:** 2025-01-18  
**Decisão:** Sprint 9 - Tarefa I1  
**Reverte:** ADR-005

---

## Contexto

No Sprint 3, dividimos o `AnalyticsRepository` original em 4 repositórios especializados (ADR-005):
- `ConversionAnalyticsRepository` (291 linhas, 3 métodos)
- `PerformanceAnalyticsRepository` (153 linhas, 2 métodos)
- `BotPerformanceAnalyticsRepository` (76 linhas, 1 método)
- `DashboardAnalyticsRepository` (95 linhas, 1 método)

**Total:** 615 linhas em 4 arquivos para 7 métodos

### Problemas Identificados

**1. Overengineering Prematuro** (DT-004)
```
UserRepository: 15 métodos → 1 arquivo → Funciona bem
AnalyticsRepository: 7 métodos → 4 arquivos → Complexidade desnecessária
```

**2. Baixa Reutilização**
- Apenas 2 consumidores principais: `MetricsService` e `DashboardController`
- Ambos precisam importar e injetar os 4 repositórios simultaneamente
- Nenhuma vantagem de modularidade realizada

**3. Navegação Degradada**
```python
# Antes (ADR-005):
from analytics.conversion_analytics_repository import ConversionAnalyticsRepository
from analytics.performance_analytics_repository import PerformanceAnalyticsRepository
from analytics.bot_performance_analytics_repository import BotPerformanceAnalyticsRepository
from analytics.dashboard_analytics_repository import DashboardAnalyticsRepository

service = MetricsService(
    conversion_repo=ConversionAnalyticsRepository(db),
    performance_repo=PerformanceAnalyticsRepository(db),
    bot_performance_repo=BotPerformanceAnalyticsRepository(db),
    dashboard_repo=DashboardAnalyticsRepository(db),
    redis_client=redis,
)

# Depois (ADR-007):
from repositories.analytics_repository import AnalyticsRepository

service = MetricsService(
    analytics_repo=AnalyticsRepository(db),
    redis_client=redis,
)
```

**4. Violação do KISS**
- Separação antecipada para evitar "God Class"
- God Class ocorre com 30+ métodos, não 7
- Adiciona complexidade sem benefício mensurável

---

## Decisão

**Consolidar os 4 repositórios em 1 arquivo:** `analytics_repository.py`

### Estrutura do Arquivo Consolidado

```python
class AnalyticsRepository:
    """Repository consolidado para todas as métricas de analytics"""

    def __init__(self, db_session: Session):
        self.db = db_session

    # =========================================================================
    # SEÇÃO 1: CONVERSION ANALYTICS (Conversão de Leads)
    # =========================================================================
    def get_conversion_rate(...)
    def get_conversion_funnel(...)
    def get_time_to_conversion(...)

    # =========================================================================
    # SEÇÃO 2: PERFORMANCE ANALYTICS (Tempo de Resposta e Volume)
    # =========================================================================
    def get_response_time_stats(...)
    def get_message_volume(...)

    # =========================================================================
    # SEÇÃO 3: BOT PERFORMANCE ANALYTICS (Autonomia do Bot)
    # =========================================================================
    def get_bot_autonomy_rate(...)

    # =========================================================================
    # SEÇÃO 4: DASHBOARD ANALYTICS (Sumários Agregados)
    # =========================================================================
    def get_dashboard_summary(...)
```

**Total:** ~520 linhas em 1 arquivo (615 → 520, -15% com docstrings melhores)

---

## Consequências

### ✅ Positivas

1. **Navegação Simplificada**
   - 1 arquivo em vez de 4 para encontrar métricas
   - Menos arquivos abertos no editor simultaneamente
   - Seções com comentários claros facilitam busca visual

2. **Redução de Imports**
   - Antes: 4 imports de repositórios
   - Depois: 1 import de repositório
   - 75% menos boilerplate de injeção de dependências

3. **Manutenção Mais Simples**
   - Métricas relacionadas ficam próximas (ex: `get_conversion_rate` e `get_conversion_funnel`)
   - Mais fácil identificar queries SQL duplicadas
   - Refatoração de código comum facilitada

4. **Sem Perda Funcional**
   - 100% dos métodos preservados
   - Mesma interface pública
   - Mesma complexidade SQL (CTEs, window functions)
   - Testes continuam passando (160/160)

### ⚠️ Negativas (Mitigadas)

1. **Arquivo Único Maior**
   - ❌ Problema: 520 linhas pode dificultar navegação
   - ✅ Mitigação: Seções com comentários de 80 colunas, separação clara de responsabilidades

2. **Risco de "God Class" Futuro**
   - ❌ Problema: Tentação de adicionar métodos não relacionados
   - ✅ Mitigação: Limite de 15 métodos (seguindo UserRepository), métodos novos devem passar code review

3. **Histórico Git Perdido**
   - ❌ Problema: `git blame` aponta para consolidação, não origem
   - ✅ Mitigação: ADR documenta origem, commits atômicos preservam contexto

---

## Métricas de Sucesso

**Antes (ADR-005):**
```
Arquivos: 4
Linhas totais: 615
Métodos: 7
Imports médios: 4 por arquivo consumidor
Complexidade ciclomática: 12
```

**Depois (ADR-007):**
```
Arquivos: 1
Linhas totais: 520 (-15%)
Métodos: 7
Imports médios: 1 por arquivo consumidor (-75%)
Complexidade ciclomática: 12 (mantida)
```

**Ganhos:**
- 📁 Arquivos: -3 (-75%)
- 📝 Linhas: -95 (-15%)
- 📦 Imports: -12 no total (-75% por consumidor)
- ⚡ Navegação: 1 arquivo em vez de 4 para procurar métricas

---

## Lições Aprendidas

### O Que Funcionou Bem

1. **Análise de Uso Prévio**
   - Grep search identificou apenas 2 consumidores
   - Confirmou baixa reutilização modular

2. **Seções com Comentários**
   - Facilita navegação em arquivo único
   - Mantém clareza sem necessidade de arquivos separados

3. **Testes Completos**
   - 160 testes garantiram zero regressão
   - Consolidação executada com confiança

### O Que Poderia Ser Melhor

1. **Evitar Divisão Prematura**
   - ADR-005 dividiu com 7 métodos (muito cedo)
   - Limite razoável: dividir após 15-20 métodos

2. **Considerar Uso Real**
   - Se todos os consumidores precisam de todos os repos, não há ganho em modularidade
   - Modularização deve seguir casos de uso reais, não teóricos

3. **God Class Não É Problema com Seções Claras**
   - 1 arquivo de 500 linhas bem organizado > 4 arquivos de 150 linhas desorganizados
   - Seções/comentários > Arquivos separados (para < 20 métodos)

---

## Alternativas Consideradas

### 1. Manter os 4 Repositórios
❌ **Rejeitada:** Adiciona complexidade sem benefício
- Não há reutilização modular
- Todos os consumidores precisam de todos os repos
- Navegação mais difícil

### 2. Consolidar em 2 Repositórios (Conversion + Performance)
❌ **Rejeitada:** Decisão arbitrária
- Ainda requer 2 imports
- Não reduz suficientemente a complexidade
- Sem critério objetivo para divisão

### 3. Consolidar em 1 Repositório (Escolhida)
✅ **Aceita:** Pragmática e suficiente
- 7 métodos cabem confortavelmente em 1 arquivo
- Seguindo padrão de UserRepository (15 métodos)
- Seções com comentários mantêm organização
- Reduz imports e navegação

---

## Referências

- ADR-005: Analytics Repository Breakdown (REVERTIDO)
- DT-004: Technical Debt - Analytics Overengineering
- UserRepository: 15 métodos, 1 arquivo, sem problemas
- KISS Principle: "Keep It Simple, Stupid"

---

## Notas de Implementação

### Arquivos Afetados
```
CRIADO:
+ src/robbot/adapters/repositories/analytics_repository.py (520 linhas)

MODIFICADO:
~ src/robbot/services/analytics/metrics_service.py (imports e __init__)
~ src/robbot/adapters/controllers/dashboard_controller.py (imports e DI)

DELETADO:
- src/robbot/adapters/repositories/analytics/conversion_analytics_repository.py
- src/robbot/adapters/repositories/analytics/performance_analytics_repository.py
- src/robbot/adapters/repositories/analytics/bot_performance_analytics_repository.py
- src/robbot/adapters/repositories/analytics/dashboard_analytics_repository.py
- src/robbot/adapters/repositories/analytics/__init__.py
- src/robbot/adapters/repositories/analytics/ (diretório vazio)
```

### Validação
```bash
# Imports sem erros
pylance: 0 errors

# Testes passando
pytest: 160/160 ✅

# Build Docker OK
docker build --target runtime-api ✅
```

---

**Conclusão:** A consolidação dos repositórios de analytics simplifica significativamente a arquitetura sem perda de funcionalidade ou clareza. Esta decisão demonstra que modularização excessiva pode ser tão prejudicial quanto código monolítico, e que a simplicidade pragmática (KISS) frequentemente supera a arquitetura teórica "ideal".
