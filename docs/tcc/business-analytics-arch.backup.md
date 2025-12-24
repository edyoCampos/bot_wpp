# 📊 Business Analytics Architecture - Bot WhatsApp Clínica

> **Data-Driven Decision Making System**  
> Arquitetura de métricas avançadas para maximizar conversão, otimizar operações e gerar vantagem competitiva.

---

## 🎯 Objetivos Estratégicos

### 1. **Maximizar Conversão de Leads**
- Identificar gargalos no funil
- Otimizar playbooks baseado em dados
- Prever probabilidade de conversão
- Reduzir taxa de abandono

### 2. **Otimizar Operações**
- Balancear carga entre secretárias
- Identificar horários de pico
- Prever demanda futura
- Reduzir tempo de resposta

### 3. **Melhorar Performance da IA**
- Medir acurácia da detecção de intenção
- Avaliar efetividade de playbooks
- Identificar falhas que causam transferência
- Otimizar scoring de maturidade

### 4. **Gerar Insights de Negócio**
- ROI por canal de aquisição
- Tendências sazonais
- Análise de concorrência (procedimentos mais demandados)
- Previsão de receita

---

## 📈 Categorias de Métricas

### **TIER 1: Core Business Metrics (Críticas)**

#### **Conversão**
- **Taxa de Conversão Global**: `(leads_convertidos / total_leads) * 100`
- **Taxa de Conversão por Etapa do Funil**
- **Tempo Médio até Conversão**: Dias entre primeiro contato e agendamento
- **Taxa de Abandono por Etapa**: Drop-off em cada fase
- **Probabilidade de Conversão por Lead** (ML-based)

#### **Receita & ROI**
- **Valor Médio por Lead Convertido** (se integrado com sistema de faturamento)
- **ROI por Canal de Aquisição**: `(receita_canal - custo_canal) / custo_canal`
- **Custo por Aquisição (CPA)**: `custo_operacional / leads_convertidos`
- **Lifetime Value (LTV)** estimado por segmento de cliente

#### **Engajamento**
- **Taxa de Resposta**: `(leads_que_responderam / total_leads_contatados) * 100`
- **Número Médio de Mensagens até Conversão**
- **Taxa de Reengajamento**: Leads que voltam a conversar após inatividade
- **Tempo Médio entre Mensagens** (mostra interesse)

### **TIER 2: Operational Excellence Metrics**

#### **Performance da Equipe**
- **Tempo Médio de Resposta** (humano)
  - Média, Mediana, P95, P99
  - Por secretária
  - Por horário do dia
- **Taxa de Resolução no Primeiro Contato**
- **Distribuição de Carga**: Conversas por secretária
- **Produtividade**: Leads convertidos por secretária por dia
- **SLA Compliance**: `% respostas dentro do SLA (ex: 5min)`

#### **Performance da IA**
- **Taxa de Autonomia do Bot**: `(conversas_resolvidas_bot / total_conversas) * 100`
- **Acurácia da Detecção de Intenção**: Comparado com validação humana
- **Taxa de Transferência para Humano**: `% conversas escaladas`
- **Motivos de Escalação** (categorizado)
- **Score Médio de Maturidade ao Converter**
- **Playbooks Mais Efetivos**: Taxa de conversão por playbook

#### **Qualidade do Atendimento**
- **Net Promoter Score (NPS)**: `% promotores - % detratores`
- **Customer Satisfaction Score (CSAT)**: Média de avaliações 1-5
- **Tempo de Resolução**: Tempo total até fechar conversa
- **Taxa de Recontato**: Leads que voltam com problemas

### **TIER 3: Advanced Analytics (Preditivas & Prescritivas)**

#### **Análise Preditiva**
- **Previsão de Demanda**: Volume esperado de mensagens próximos 7-30 dias
- **Probabilidade de Conversão por Lead** (ML model)
  - Features: tempo resposta, score maturidade, número mensagens, horário contato
- **Churn Risk**: Probabilidade de lead abandonar processo
- **Melhor Horário para Reengajamento** por segmento

#### **Análise Prescritiva**
- **Recomendação de Playbook**: Qual playbook usar para maximizar conversão
- **Alocação Ótima de Secretárias**: Distribuir carga baseado em skills
- **Pricing Optimization**: Procedimentos com maior elasticidade de demanda
- **Budget Allocation**: Onde investir marketing para maior ROI

#### **Análise de Tendências**
- **Sazonalidade**: Procedimentos por época do ano
- **Tendências de Mercado**: Crescimento por tipo de procedimento
- **Análise de Concorrência**: Comparar métricas com benchmarks do setor
- **Forecasting de Receita**: Projeção 3-6 meses baseado em pipeline

---

## 🏗️ Arquitetura Técnica

### **Camada 1: Data Collection**

```python
# Já implementado:
- conversations (status, timestamps, lead_id)
- conversation_messages (direction, content, timestamp)
- leads (maturity_score, status, assigned_to, converted_at)
- llm_interactions (intent, confidence, tokens)
- lead_interactions (type, outcome, duration)

# A implementar:
- feedback (conversation_id, score, nps_score, comment)
- marketing_campaigns (channel, cost, leads_generated)
- procedure_bookings (lead_id, procedure, value, booked_at)
```

### **Camada 2: Data Processing**

#### **Aggregation Service** (Redis + PostgreSQL)
```python
class MetricsAggregationService:
    """
    Agrega métricas em tempo real e batch.
    
    - Real-time: Redis (TTL 5min) para dashboard
    - Historical: PostgreSQL (materialized views) para relatórios
    """
    
    async def aggregate_hourly():
        """Roda a cada hora via RQ scheduler"""
        
    async def aggregate_daily():
        """Roda à meia-noite via RQ scheduler"""
```

#### **Metrics Calculator**
```python
class MetricsCalculator:
    """Cálculos complexos de métricas"""
    
    def calculate_conversion_funnel()
    def calculate_lead_scoring()
    def calculate_nps()
    def calculate_roi_by_channel()
```

### **Camada 3: Analytics API**

#### **Endpoints REST**

**Dashboard Core:**
```
GET /api/v1/metrics/dashboard/summary
GET /api/v1/metrics/dashboard/realtime
GET /api/v1/metrics/dashboard/trends?period=30d
```

**Conversion Analytics:**
```
GET /api/v1/analytics/conversion-funnel
GET /api/v1/analytics/conversion-rate?segment=procedure
GET /api/v1/analytics/abandonment-analysis
GET /api/v1/analytics/time-to-conversion
```

**Performance Analytics:**
```
GET /api/v1/analytics/team-performance
GET /api/v1/analytics/bot-performance
GET /api/v1/analytics/sla-compliance
GET /api/v1/analytics/response-time-distribution
```

**Predictive Analytics:**
```
GET /api/v1/analytics/demand-forecast?days=30
GET /api/v1/analytics/lead-score?lead_id=uuid
GET /api/v1/analytics/churn-risk
POST /api/v1/analytics/what-if-analysis
```

**Business Intelligence:**
```
GET /api/v1/analytics/roi-by-channel
GET /api/v1/analytics/revenue-forecast
GET /api/v1/analytics/procedure-trends
GET /api/v1/analytics/competitive-analysis
```

### **Camada 4: Visualization & Export**

```python
# Formatters para diferentes consumidores
- JSON: Dashboard web
- CSV/Excel: Exportação para análise externa
- PDF: Relatórios executivos
- Grafana: Monitoramento em tempo real
```

---

## 🧮 Fórmulas e Algoritmos

### **1. Score de Probabilidade de Conversão (ML)**

```python
def calculate_conversion_probability(lead: Lead, conversation: Conversation) -> float:
    """
    Random Forest ou Gradient Boosting com features:
    
    Features:
    - maturity_score (0-100)
    - response_time_avg (seconds)
    - message_count (int)
    - engagement_score (custom)
    - days_since_first_contact (int)
    - hour_of_day (0-23)
    - day_of_week (0-6)
    - playbook_effectiveness (histórico)
    
    Target: converted (0/1)
    
    Returns: probability (0.0 - 1.0)
    """
    # Implementação com scikit-learn
```

### **2. Forecasting de Demanda (Prophet)**

```python
from fbprophet import Prophet

def forecast_message_volume(days_ahead: int = 30) -> DataFrame:
    """
    Previsão de volume de mensagens usando Prophet (Facebook).
    
    Considera:
    - Sazonalidade diária (horários de pico)
    - Sazonalidade semanal (fins de semana vs dias úteis)
    - Sazonalidade anual (férias, verão)
    - Tendência de crescimento
    - Feriados customizados
    
    Returns: DataFrame com ds (date), yhat (predicted), yhat_lower, yhat_upper
    """
```

### **3. Otimização de Alocação (Linear Programming)**

```python
from scipy.optimize import linprog

def optimize_team_allocation(
    secretaries: List[User],
    expected_volume: int,
    constraints: Dict
) -> Dict[int, int]:
    """
    Alocação ótima de secretárias para minimizar tempo de resposta.
    
    Objetivo: Minimizar (avg_response_time * cost_per_secretary)
    
    Restrições:
    - Cada secretária tem capacidade máxima
    - Mínimo de secretárias por turno
    - Skills específicas (ex: ortodontia)
    
    Returns: {user_id: allocated_conversations}
    """
```

### **4. Anomaly Detection (Z-Score)**

```python
def detect_anomalies(metric: str, window_days: int = 30) -> List[Anomaly]:
    """
    Detecta anomalias usando Z-score (desvio padrão).
    
    Anomalia se: |z_score| > 2.5 (99% confiança)
    
    z_score = (value - mean) / std_dev
    
    Returns: Lista de anomalias com severity (low/medium/high/critical)
    """
```

---

## 📊 Dashboards Propostos

### **1. Executive Dashboard (CEO/Diretor)**
- KPIs principais (conversão, receita, ROI)
- Tendências mês a mês
- Alertas críticos
- Forecast de receita

### **2. Operations Dashboard (Gerente)**
- Performance da equipe
- SLA compliance
- Distribuição de carga
- Alertas de anomalias

### **3. Marketing Dashboard**
- ROI por canal
- Custo por aquisição
- Procedimentos mais demandados
- Análise de campanhas

### **4. AI Performance Dashboard (Tech Lead)**
- Taxa de autonomia do bot
- Acurácia de intenção
- Playbooks performance
- Logs de erros

### **5. Secretary Dashboard (Secretária)**
- Minhas métricas
- Comparação com média da equipe
- Meus leads prioritários
- Feedback de clientes

---

## 🔐 Segurança e Privacidade

### **Access Control**
```python
# Role-based access
- ADMIN: Acesso total a todas métricas
- MANAGER: Métricas da equipe, sem dados sensíveis de leads
- SECRETARY: Apenas suas próprias métricas
- MARKETING: Apenas métricas de aquisição e conversão

# Data masking
- Telefones mascarados: 5511****9999
- Nomes: Apenas iniciais para não-admins
```

### **LGPD Compliance**
- Anonimização de dados para análises agregadas
- Retenção de dados: 2 anos históricos
- Right to be forgotten: Exclusão cascata de métricas

---

## 🚀 Roadmap de Implementação

### **Fase 1: Core Metrics (Sprint 1-2)** ✅ PRÓXIMO
- [ ] MetricsService base
- [ ] Dashboard summary endpoint
- [ ] Conversion funnel
- [ ] Response time analytics
- [ ] Basic caching (Redis)

### **Fase 2: Advanced Metrics (Sprint 3-4)**
- [ ] Team performance analytics
- [ ] Bot performance metrics
- [ ] NPS collection & calculation
- [ ] SLA monitoring

### **Fase 3: Predictive Analytics (Sprint 5-6)**
- [ ] Demand forecasting (Prophet)
- [ ] Lead scoring (ML model)
- [ ] Anomaly detection
- [ ] Optimization algorithms

### **Fase 4: Business Intelligence (Sprint 7-8)**
- [ ] ROI analysis
- [ ] Revenue forecasting
- [ ] Competitive analysis
- [ ] Executive reports

---

## 📚 Tech Stack Recomendado

### **Analytics Engine**
- **PostgreSQL**: Dados históricos + Materialized Views
- **Redis**: Cache de métricas (TTL 5min)
- **Pandas**: Data manipulation
- **NumPy**: Cálculos estatísticos

### **Machine Learning**
- **scikit-learn**: Lead scoring, clustering
- **Prophet**: Time series forecasting
- **TensorFlow/PyTorch**: Deep learning (futuro)

### **Visualization**
- **FastAPI**: APIs REST
- **Plotly**: Gráficos interativos (JSON)
- **Grafana**: Real-time monitoring
- **Apache Superset**: BI self-service (futuro)

### **Export & Reporting**
- **pandas**: CSV/Excel export
- **ReportLab**: PDF generation
- **Jinja2**: Email templates

---

## 💡 Métricas Inovadoras (Diferenciais)

### **1. Engagement Decay Score**
```python
engagement_decay = exp(-days_since_last_message / decay_rate)
```
Prediz quando um lead está "esfriando" para reengajamento proativo.

### **2. Playbook Effectiveness Matrix**
```
           | High Intent | Low Intent
-----------+-------------+------------
High Score |   CONVERT   |  NURTURE
Low Score  |   PUSH      |  DISCARD
```
Classifica leads para ação ótima.

### **3. Channel Attribution Multi-Touch**
Credita conversão proporcionalmente a todos canais no customer journey.

### **4. Predictive LTV per Segment**
Estima valor de vida do cliente por tipo de procedimento.

### **5. Seasonal Procedure Index**
```python
index = (current_demand / baseline_demand) * 100
```
Identifica quando fazer promoções.

---

## 🎓 Glossário de Métricas

- **Conversion Rate**: % de leads que agendam consulta
- **Drop-off Rate**: % que abandonam em cada etapa do funil
- **NPS**: Net Promoter Score (-100 a +100)
- **CSAT**: Customer Satisfaction Score (1-5)
- **CPA**: Custo Por Aquisição (R$)
- **LTV**: Lifetime Value do cliente (R$)
- **CAC**: Custo de Aquisição de Cliente (R$)
- **Churn**: Taxa de abandono/cancelamento (%)
- **MAU**: Monthly Active Users (leads ativos no mês)
- **DAU**: Daily Active Users (leads ativos no dia)
- **P95**: 95º percentil (95% dos valores estão abaixo)

---

**Última atualização:** 18/12/2025  
**Versão:** 1.0  
**Autor:** AI + Business Analytics
