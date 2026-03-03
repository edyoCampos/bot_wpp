# Script de demonstração - Queries formatadas para apresentação (PowerShell)
# Uso: pwsh -File demo-queries.ps1

Write-Host "QUERIES DE DEMONSTRACAO - BOT WHATSAPP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Última conversa completa (formatada)
Write-Host "1. ULTIMA CONVERSA COMPLETA" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Yellow
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT ROW_NUMBER() OVER (ORDER BY created_at) as num, CASE direction WHEN 'INBOUND' THEN '>> Cliente' WHEN 'OUTBOUND' THEN '<< Bot' END as origem, SUBSTRING(REPLACE(body, E'\n', ' '), 1, 100) || CASE WHEN LENGTH(body) > 100 THEN '...' ELSE '' END as mensagem, TO_CHAR(created_at - INTERVAL '3 hours', 'DD/MM HH24:MI:SS') as hora FROM conversation_messages WHERE conversation_id = (SELECT id FROM conversations ORDER BY updated_at DESC LIMIT 1) ORDER BY created_at;"
Write-Host ""
Read-Host "Pressione ENTER para continuar"

# 2. Estatísticas das últimas 24h
Write-Host "`n2. ESTATISTICAS - ULTIMAS 24H" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT COUNT(*) FILTER (WHERE direction = 'INBOUND') as recebidas, COUNT(*) FILTER (WHERE direction = 'OUTBOUND') as enviadas, COUNT(DISTINCT conversation_id) as conversas, TO_CHAR(MIN(created_at) - INTERVAL '3 hours', 'HH24:MI') as primeira, TO_CHAR(MAX(created_at) - INTERVAL '3 hours', 'HH24:MI') as ultima FROM conversation_messages WHERE created_at > NOW() - INTERVAL '24 hours';"
Write-Host ""
Read-Host "Pressione ENTER para continuar"

# 3. Últimas 5 mensagens (todas conversas)
Write-Host "`n3. ULTIMAS 5 MENSAGENS (TODAS CONVERSAS)" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Yellow
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT CASE direction WHEN 'INBOUND' THEN '>> Cliente' WHEN 'OUTBOUND' THEN '<< Bot' END as dir, from_phone as telefone, SUBSTRING(REPLACE(body, E'\n', ' '), 1, 60) || '...' as mensagem, TO_CHAR(created_at - INTERVAL '3 hours', 'DD/MM HH24:MI') as quando FROM conversation_messages ORDER BY created_at DESC LIMIT 5;"
Write-Host ""
Read-Host "Pressione ENTER para continuar"

# 4. Leads criados hoje
Write-Host "`n4. LEADS CRIADOS HOJE" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT name as nome, phone_number as telefone, status, maturity_score as score, TO_CHAR(created_at - INTERVAL '3 hours', 'HH24:MI') as criado FROM leads WHERE (created_at - INTERVAL '3 hours')::date = (NOW() - INTERVAL '3 hours')::date ORDER BY created_at DESC;"
Write-Host ""
Read-Host "Pressione ENTER para continuar"

# 5. Fila de jobs RQ
Write-Host "`n5. FILA DE PROCESSAMENTO (RQ)" -ForegroundColor Yellow
Write-Host "---------------------------------" -ForegroundColor Yellow
Write-Host "Mensagens na fila:"
docker-compose exec -T redis redis-cli LLEN rq:queue:messages
Write-Host "`nJobs AI na fila:"
docker-compose exec -T redis redis-cli LLEN rq:queue:ai
Write-Host "`nEscalacoes na fila:"
docker-compose exec -T redis redis-cli LLEN rq:queue:escalation
Write-Host ""
Read-Host "Pressione ENTER para continuar"

# 6. Conversas por fase SPIN
Write-Host "`n6. MATURIDADE - DISTRIBUICAO SPIN" -ForegroundColor Yellow
Write-Host "------------------------------------" -ForegroundColor Yellow
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT CASE WHEN maturity_score < 30 THEN 'SITUATION (0-29)' WHEN maturity_score < 50 THEN 'PROBLEM (30-49)' WHEN maturity_score < 75 THEN 'IMPLICATION (50-74)' WHEN maturity_score < 85 THEN 'NEED-PAYOFF (75-84)' ELSE 'READY (85-100)' END as fase_spin, COUNT(*) as quantidade, ROUND(AVG(maturity_score), 1) as score_medio FROM leads WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY fase_spin ORDER BY MIN(CASE WHEN maturity_score < 30 THEN 1 WHEN maturity_score < 50 THEN 2 WHEN maturity_score < 75 THEN 3 WHEN maturity_score < 85 THEN 4 ELSE 5 END);"

Write-Host "`nDEMONSTRACAO CONCLUIDA!" -ForegroundColor Green
Write-Host ""
