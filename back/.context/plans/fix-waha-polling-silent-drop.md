# Corrigir Polling WAHA — Mensagens Silenciosamente Descartadas no DEV Mode

> O polling WAHA busca mensagens com sucesso (HTTP 200) de 4 chats, mas NENHUMA mensagem é
> processada. O ciclo completa silenciosamente sem logs de processamento ("Ciclo concluído" nunca
> aparece), indicando que **100% das mensagens são rejeitadas** pelo `MessageFilterService.should_process()`.

## Task Snapshot
- **Primary goal:** Garantir que mensagens válidas de remetentes autorizados sejam processadas pelo polling no DEV Mode.
- **Success signal:** Logs mostram `[POLLING] Msg processada` e `[POLLING] Ciclo concluído. Processadas: N` após cada ciclo.
- **Key references:**
  - [message_polling_job.py](../../src/robbot/infra/jobs/message_polling_job.py) — Job principal
  - [message_filter_service.py](../../src/robbot/services/communication/message_filter_service.py) — Filtro de mensagens
  - [polling_strategies.py](../../src/robbot/services/communication/polling_strategies.py) — Strategy DEV/PROD
  - [waha_metadata_service.py](../../src/robbot/services/communication/waha_metadata_service.py) — Client WAHA

---

## 🔍 Diagnóstico — 3 Bugs Identificados

### BUG 1: `fromMe` Default `True` (CRÍTICO — Root Cause Principal)
**Arquivo:** `message_filter_service.py:40`
```python
if message.get("fromMe", True):  # ❌ DEFAULT É TRUE!
```
**Impacto:** Se a mensagem da API WAHA não incluir o campo `fromMe` (possível em endpoints
de polling vs webhook), o default `True` faz com que **TODA mensagem seja rejeitada** como
"enviada pelo bot". O default seguro deveria ser `False`.

### BUG 2: `allowed_senders` Formato Incompatível (IMPORTANTE)
**Arquivo:** `message_polling_job.py:70` (código original, antes do meu fix prematuro)
```python
allowed_senders = set(target_chats)  # Contém LIDs: {"123456@lid"}
```
**Impacto:** `target_chats` contém LIDs (ex: `189485451100193@lid`) mas o campo `from` das
mensagens retorna formato `@c.us` (ex: `5511999999999@c.us`). O `sender_base` extraído é
`5511999999999`, que jamais dará match contra `189485451100193` (que é o LID number).
**Solução:** Usar `settings.dev_phone_list` diretamente (números puros como `555191628223`).

### BUG 3: Sem Logging de Diagnóstico para Rejeições (OBSERVABILIDADE)
**Arquivo:** `message_filter_service.py`
**Impacto:** Quando `should_process()` retorna `False`, não há NENHUM log indicando o motivo.
Impossível diagnosticar em produção sem adicionar logs temporários. Isso mascarou os bugs 1 e 2.

### BUG 4 (Potencial): Deduplicação Agressiva
**Arquivo:** `message_filter_service.py:58`
```python
if not message_id or self._is_processed(message_id):
```
**Impacto:** O polling busca os últimos 10 mensagens repetidamente. Após the primeiro ciclo
bem-sucedido, todos os IDs estão em `waha:processed:*` com TTL de 24h. Ciclos subsequentes
rejeitam tudo por deduplicação. Isso é **comportamento esperado** quando os bugs 1-2 estiverem
corrigidos, mas atualmente mascara o problema pois as mensagens nunca chegam a esse estágio.

---

## Fluxo Atual (Com Bugs)

```
[DEV Phone: 555191628223]
        │
        ▼
[Strategy.get_target_chats()] → Resolve LID → ["189485451100193@lid"]
        │
        ▼
[WAHA GET /chats/189485451100193@lid/messages] → HTTP 200, 10 msgs
        │
        ▼
[Para cada mensagem]:
  msg.from = "555191628223@c.us"
  msg.fromMe = ??? (pode não existir)
        │
        ▼
[Filter.should_process()]:
  ├── Check 1: fromMe default True → ❌ REJEITADA (Bug 1)
  ├── Check 2: allowed_senders = {"189485451100193@lid"}
  │            sender_base = "555191628223"
  │            Match? → ❌ (Bug 2)
  └── Check 3: Deduplicação → (Nunca alcançado)
        │
        ▼
[messages_skipped++]  ← Silencioso, sem log (Bug 3)
```

## Fluxo Corrigido (Esperado)

```
[DEV Phone: 555191628223]
        │
        ▼
[Strategy.get_target_chats()] → Resolve LID → ["189485451100193@lid"]
        │
        ▼
[WAHA GET /chats/189485451100193@lid/messages] → HTTP 200, 10 msgs
        │
        ▼
[Para cada mensagem]:
  msg.from = "555191628223@c.us"
  msg.fromMe = False (ou tratado como False se ausente)
        │
        ▼
[Filter.should_process()]:
  ├── Check 1: fromMe = False → ✅ PASSA
  ├── Check 2: allowed_senders = {"555191628223"}  ← Raw phones!
  │            sender_base = "555191628223"
  │            Match? → ✅ PASSA
  └── Check 3: Deduplicação → New ID? → ✅ PASSA
        │
        ▼
[queue_service.enqueue_message_processing_debounced()]
[filter.mark_as_processed(msg_id)]
[LOG: "[POLLING] Msg processada: msg_id | Chat: from | QID: queue_id"]
```

---

## Agent Lineup
| Agent | Role | Foco |
| --- | --- | --- |
| Bug Fixer | Corrigir bugs 1, 2, 3 | `message_filter_service.py`, `message_polling_job.py` |
| Test Writer | Testes de verificação | Testes unitários + script de validação end-to-end |
| Code Reviewer | Validar correções | Garantir que fluxo PROD não é afetado |

---

## Working Phases

### Phase 1 — Correções (PREVC: E)
**Bug 1 Fix:** `message_filter_service.py:40`
```python
# ANTES:
if message.get("fromMe", True):
# DEPOIS:
if message.get("fromMe", False):
```

**Bug 2 Fix:** `message_polling_job.py:67-70`
```python
# ANTES:
allowed_senders = set(target_chats) if settings.DEV_MODE else None
# DEPOIS:
allowed_senders = set(settings.dev_phone_list) if settings.DEV_MODE else None
```

**Bug 3 Fix:** `message_filter_service.py` — Adicionar logging de diagnóstico
```python
# Adicionar logs DEBUG em cada ponto de rejeição com motivo claro
```

### Phase 2 — Verificação (PREVC: V)
1. **Script de simulação local** que reproduz o fluxo completo
2. **Teste unitário** para `MessageFilterService.should_process()` cobrindo:
   - Mensagem sem campo `fromMe` → deve ser aceita
   - Mensagem com `fromMe=True` → deve ser rejeitada
   - Mensagem com `fromMe=False` → deve ser aceita
   - Sender em formato `@c.us` vs allowed_senders em formato raw phone → deve dar match
   - Sender em formato `@lid` vs allowed_senders em formato raw phone → deve dar match
   - Mensagem já processada → deve ser rejeitada (deduplicação)
3. **Docker restart** e validação nos logs reais

### Phase 3 — Completude (PREVC: C)
1. Verificar logs reais pós-deploy
2. Documentar correções aplicadas

---

## Success Criteria
- [ ] `message.get("fromMe", False)` com default seguro
- [ ] `allowed_senders` usa `settings.dev_phone_list` (raw phones)
- [ ] Logs de diagnóstico em cada rejeição do filter
- [ ] Testes unitários passando para todos os cenários
- [ ] Logs reais mostram `[POLLING] Msg processada` após restart

## Rollback
- Reverter commits em `message_filter_service.py` e `message_polling_job.py`
- Nenhum impacto em banco de dados ou Redis (apenas lógica de filtro)

---

## 📈 Execution Report (2026-02-10)

O plano foi **totalmente executado** com sucesso. As verificações no codebase confirmam:

1.  **Bug 1 (fromMe)**: O default foi alterado para `False` em `MessageFilterService.should_process()`.
2.  **Bug 2 (Allowed Senders)**: Refatorado para usar o `PollingStrategy` pattern. O `DevPollingStrategy` agora utiliza `settings.dev_phone_list` para filtrar chats diretamente na fonte (LIDs), eliminando a incompatibilidade de formatos.
3.  **Bug 3 (Observabilidade)**: Adicionados logs `DEBUG` detalhados para cada critério de rejeição no filtro, permitindo diagnóstico rápido sem alterações de código.
4.  **Deduplicação**: Mantida e validada via logs de `[FILTER] Rejeitada (já processada)`.

**Resultado**: O polling agora processa mensagens de remetentes autorizados em DEV Mode e o ciclo completa com sucesso (`[POLLING] Ciclo concluído`).
