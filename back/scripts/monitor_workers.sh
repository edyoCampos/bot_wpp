#!/bin/bash
# Monitor de Workers RQ - Mostra carga das filas em tempo real

echo "=========================================="
echo "📊 Monitor de Workers e Filas RQ"
echo "=========================================="
echo ""

# Conectar ao Redis e mostrar estatísticas
docker exec redis redis-cli <<EOF
echo "🔢 JOBS NAS FILAS:"
echo "  messages: " LLEN rq:queue:messages
echo "  ai: " LLEN rq:queue:ai
echo "  escalation: " LLEN rq:queue:escalation
echo "  failed: " LLEN rq:queue:failed
echo ""
echo "👷 WORKERS ATIVOS:"
SMEMBERS rq:workers
echo ""
echo "⏱️  JOBS SENDO PROCESSADOS AGORA:"
SMEMBERS rq:workers:started
echo ""
echo "📈 TOTAL DE JOBS PROCESSADOS:"
GET rq:stat:processed
GET rq:stat:failed
EOF

echo ""
echo "=========================================="
echo "💡 Dica: Execute 'watch -n 2 ./scripts/monitor_workers.sh' para atualização contínua"
echo "=========================================="
