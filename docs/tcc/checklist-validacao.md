# ✅ CHECKLIST DE VALIDAÇÃO - Testes Bot WhatsApp

> **Copie este checklist e marque cada item conforme testa**

---

## 🔧 PRÉ-REQUISITOS

- [ ] Docker e Docker Compose instalados
- [ ] Containers rodando (`docker ps` mostra 6 serviços UP)
- [ ] API healthy (http://localhost:3333/api/v1/health retorna "ok")
- [ ] Swagger acessível (http://localhost:3333/docs)
- [ ] Postman Collection importada (opcional)
- [ ] Token JWT obtido e configurado no Swagger

---

## 📚 FASE 1: INFRAESTRUTURA E AUTENTICAÇÃO

- [ ] **UC-001**: Health Check → Status 200, todos components.ok = true
- [ ] **UC-002**: Signup Admin → Status 201, role = "admin"
- [ ] **UC-003**: Login → Status 200, access_token presente
- [ ] **UC-004**: Get Me → Status 200, dados do admin retornados
- [ ] **UC-005**: Signup Secretária → Status 201, role = "user"

**✅ FASE 1 COMPLETA: Sistema de autenticação funcional**

---

## 📚 FASE 2: INTEGRAÇÃO WAHA (WhatsApp)

- [ ] **UC-006**: Criar Sessão → Status 201, webhook configurado
- [ ] **UC-007**: Iniciar Sessão → Status 200, QR code presente
  - [ ] **MANUAL**: QR Code escaneado no celular
  - [ ] **MANUAL**: Status mudou para "WORKING" após scan
- [ ] **UC-008**: Verificar Status → Status 200, status = "WORKING"
- [ ] **UC-009**: Listar Sessões → Status 200, sessão criada na lista

**✅ FASE 2 COMPLETA: WhatsApp conectado e pronto**

---

## 📚 FASE 3: PLAYBOOKS (Mensagens Pré-Aprovadas)

- [ ] **UC-010**: Criar Tópico → Status 201, UUID válido gerado
- [ ] **UC-011**: Criar Playbook → Status 201, vinculado ao tópico
- [ ] **UC-012**: Adicionar Msg Texto → Status 201, order = 1
- [ ] **UC-013**: Adicionar Msg Imagem → Status 201, media_url presente
- [ ] **UC-014**: Buscar Playbooks → Status 200, relevance_score presente
- [ ] **UC-015**: Obter Passos → Status 200, 2 mensagens ordenadas

**✅ FASE 3 COMPLETA: Sistema de playbooks funcional**

---

## 📚 FASE 4: MENSAGENS E MÍDIA

- [ ] **UC-016**: Mensagem Texto → Status 201, type = "text"
- [ ] **UC-017**: Áudio (Faster-Whisper) → Status 201
  - [ ] transcription presente
  - [ ] Texto em português correto
  - [ ] Processamento automático
- [ ] **UC-018**: Imagem (BLIP-2) → Status 201
  - [ ] title gerado
  - [ ] description combinando caption + análise
  - [ ] tags contextuais (food, meal, etc)
  - [ ] Análise local (zero custo)
- [ ] **UC-019**: Vídeo → Status 201
  - [ ] transcription do áudio presente
  - [ ] Metadata básico gerado
- [ ] **UC-020**: Localização → Status 201
  - [ ] Coordenadas corretas (Dois Irmãos/RS)
  - [ ] title presente

**✅ FASE 4 COMPLETA: Processamento de mídia funcional**

---

## 📚 FASE 5: CONVERSAS E LEADS

- [ ] **UC-021**: Simular Webhook → Status 202 (Accepted)
  - [ ] log_id presente
  - [ ] Worker processou (ver logs: `docker logs wpp_bot-worker-1`)
  - [ ] Logs mostram: "✓ Mensagem processada com sucesso"
- [ ] **UC-022**: Verificar Conversa → Status 200
  - [ ] Conversa criada automaticamente
  - [ ] Lead criado e vinculado
  - [ ] maturity_score inicial correto
  - [ ] messages_count = 2 (inbound + outbound)
- [ ] **UC-023**: Ver Mensagens → Status 200
  - [ ] 2 mensagens retornadas
  - [ ] direction correto (inbound/outbound)
  - [ ] Resposta bot usando SPIN Selling
- [ ] **UC-024**: Ver Lead → Status 200
  - [ ] Lead criado com phone_number
  - [ ] status = "new"
  - [ ] maturity_score incrementado
- [ ] **UC-025**: Ver Interações → Status 200
  - [ ] Interação registrada
  - [ ] type = intenção detectada

**✅ FASE 5 COMPLETA: Fluxo de conversação funcional**

---

## 📚 FASE 6: GEMINI AI E CONTEXTO (CRÍTICO) 🎯

- [ ] **UC-026**: Conversa SPIN - PROBLEM → Status 202
  - [ ] Bot detecta fase PROBLEM
  - [ ] Pergunta aprofunda dor (metodologia SPIN)
  - [ ] maturity_score aumentou
  - [ ] Contexto mantido (ChromaDB)
- [ ] **UC-027**: Conversa SPIN - IMPLICATION → Status 202
  - [ ] Bot detecta fase IMPLICATION
  - [ ] Pergunta explora impactos/urgência
  - [ ] maturity_score alto (~30-40)
  - [ ] Possível urgência detectada
- [ ] **UC-028**: Agendamento → Status 202
  - [ ] Intenção: AGENDAMENTO detectada
  - [ ] maturity_score alto (>50)
  - [ ] Bot fornece informações práticas
  - [ ] Possível uso de Playbook Tools
- [ ] **UC-029**: Gemini Tool Localização 📍 → Status 202
  - [ ] Gemini detecta "onde fica", "localização"
  - [ ] Tool send_clinic_location executada
  - [ ] Pin WhatsApp enviado (ver logs WAHA)
  - [ ] Coordenadas corretas
- [ ] **UC-030**: Logs LLM → Status 200
  - [ ] Todas interações registradas
  - [ ] tokens_used presente (custo)
  - [ ] latency_ms presente (performance)

**✅ FASE 6 COMPLETA: IA conversacional funcional (CORE DO SISTEMA)**

---

## 📚 FASE 7: ESCALAÇÃO PARA HUMANO

- [ ] **UC-031**: Atribuir Conversa → Status 200
  - [ ] assigned_to atualizado
  - [ ] status = "escalated"
- [ ] **UC-032**: Ver Notificações → Status 200
  - [ ] Notificação presente
  - [ ] type = "conversation_assigned"
  - [ ] is_read = false
- [ ] **UC-033**: Marcar Lida → Status 200
  - [ ] is_read = true
  - [ ] read_at timestamp

**✅ FASE 7 COMPLETA: Sistema de transferência funcional**

---

## 📚 FASE 8: TAGS E FILTROS

- [ ] **UC-034**: Adicionar Tags → Status 200
  - [ ] 4 tags associadas
  - [ ] Tags criadas automaticamente
- [ ] **UC-035**: Filtrar por Tag → Status 200
  - [ ] Apenas conversas com tag filtrada
  - [ ] Filtros combinados funcionando

**✅ FASE 8 COMPLETA: Sistema de categorização funcional**

---

## 📚 FASE 9: MÉTRICAS E ANALYTICS

- [ ] **UC-036**: Métricas Gerais → Status 200
  - [ ] Todas as métricas presentes
  - [ ] Valores corretos baseados nos testes
- [ ] **UC-037**: Métricas por Período → Status 200
  - [ ] Filtro de data funcionando
  - [ ] period correto
- [ ] **UC-038**: Métricas por Campanha → Status 200
  - [ ] Métricas por origem
  - [ ] ROI calculado (cost_per_conversion)

**✅ FASE 9 COMPLETA: Dashboard de métricas funcional**

---

## 📚 FASE 10: GESTÃO DE FILAS

- [ ] **UC-039**: Status Filas → Status 200
  - [ ] 3 filas presentes (messages, ai, escalation)
  - [ ] size e failed_count corretos
  - [ ] Workers rodando
- [ ] **UC-040**: Reprocessar Job → Status 200
  - [ ] Job re-enfileirado com sucesso

**✅ FASE 10 COMPLETA: Sistema de filas funcional**

---

## 🔥 TESTES CRÍTICOS (Mínimo Viável)

Se tiver pouco tempo, valide APENAS estes 10:

- [ ] ✅ **UC-001**: Health Check
- [ ] 🔐 **UC-003**: Login JWT
- [ ] 📱 **UC-006**: Criar Sessão WhatsApp
- [ ] 🎤 **UC-017**: Transcrição Faster-Whisper
- [ ] 🖼️ **UC-018**: Análise BLIP-2
- [ ] 💬 **UC-021**: Webhook Inbound
- [ ] 🧠 **UC-026**: Conversa SPIN (IA)
- [ ] 📍 **UC-029**: Gemini Tool Localização
- [ ] 📊 **UC-036**: Métricas Dashboard
- [ ] ⚙️ **UC-039**: Filas Redis

**Se TODOS os 10 passarem → Sistema 100% funcional!**

---

## 📊 MÉTRICAS DE QUALIDADE

### Performance ✅
- [ ] API response time médio < 500ms
- [ ] Webhook processing < 10s end-to-end
- [ ] Gemini latency < 3s (95º percentil)
- [ ] Faster-Whisper < 5s (áudio 30s)
- [ ] BLIP-2 < 5s (imagem padrão)

### Erros ✅
- [ ] 0 erros 500 (Internal Server Error)
- [ ] 0 erros 404 (Not Found) em endpoints válidos
- [ ] 0 falhas de autenticação inesperadas
- [ ] 0 jobs travados no Redis Queue

### Funcionalidade ✅
- [ ] Respostas do bot fluidas (não robóticas)
- [ ] Detecção de intenção precisa (>85%)
- [ ] Contexto conversacional mantido
- [ ] Transcrição de áudio em português correto
- [ ] Análise de imagem coerente
- [ ] Gemini Tools executando automaticamente

---

## 🐛 BUGS ENCONTRADOS

**Use este espaço para documentar bugs**:

### BUG-001:
- UC afetado:
- Severidade:
- Descrição:
- Steps to reproduce:
- Prioridade:

### BUG-002:
- UC afetado:
- Severidade:
- Descrição:
- Steps to reproduce:
- Prioridade:

---

## 📈 PROGRESSO GERAL

**Total de Casos de Uso**: 44  
**Casos Testados**: ___ / 44  
**Casos Passando**: ___ / ___  
**Taxa de Sucesso**: ____%

**Bugs Encontrados**:
- P0 (Bloqueadores): ___
- P1 (Críticos): ___
- P2 (Importantes): ___
- P3 (Nice to have): ___

---

## ✅ VALIDAÇÃO FINAL

Marque APENAS quando 100% confiante:

- [ ] Sistema está 100% funcional
- [ ] Todos os casos de uso críticos passando
- [ ] Performance aceitável (< targets)
- [ ] Zero bugs P0 ou P1
- [ ] Documentação atualizada
- [ ] Pronto para deploy em produção

**Data de Conclusão**: ___________  
**Testado por**: ___________  
**Aprovado por**: ___________

---

## 🚀 PRÓXIMOS PASSOS

- [ ] Corrigir bugs P0 e P1 encontrados
- [ ] Otimizar performance (se necessário)
- [ ] Testes de carga (100+ usuários simultâneos)
- [ ] Testes E2E completos (WhatsApp real → Agendamento)
- [ ] Deploy em ambiente de staging
- [ ] Testes finais em staging
- [ ] Deploy em produção
- [ ] Monitoramento pós-deploy (7 dias)

---

**📋 Imprima este checklist e marque conforme testa!**
