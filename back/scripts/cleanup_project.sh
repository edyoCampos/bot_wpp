#!/bin/bash
# Script de limpeza do projeto
# Remove arquivos temporários, cache Python e diretórios vazios

echo "🧹 Iniciando limpeza do projeto..."

# Remover __pycache__ e .pyc
echo "📦 Removendo cache Python..."
find ./src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ./tests -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ./src -type f -name "*.pyc" -delete 2>/dev/null || true
find ./tests -type f -name "*.pyc" -delete 2>/dev/null || true

# Remover .pytest_cache
echo "🧪 Removendo cache de testes..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Remover diretórios vazios
echo "📁 Removendo diretórios vazios..."
find ./src -type d -empty -delete 2>/dev/null || true

# Remover logs temporários
echo "📝 Removendo logs temporários..."
find . -type f -name "*.log" -path "*/logs/*" -delete 2>/dev/null || true
find . -type f -name "*crash*.log" -delete 2>/dev/null || true

# Remover arquivos de backup
echo "💾 Removendo backups..."
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true

# Remover .DS_Store (macOS)
echo "🍎 Removendo arquivos do macOS..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

# Remover arquivos de debug da raiz (criados durante troubleshooting)
echo "🐛 Removendo arquivos de debug..."
rm -f ./*.txt 2>/dev/null || true
rm -f ./check_*.py ./test_*.py ./find_*.py ./verify_*.py ./trigger_*.py ./cleanup_*.py 2>/dev/null || true
rm -f ./CLEANUP_REPORT.md ./AGENTS.md 2>/dev/null || true

# Estatísticas finais
echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📊 Estatísticas:"
echo "   - Diretórios Python: $(find ./src -type d | wc -l)"
echo "   - Arquivos Python: $(find ./src -type f -name "*.py" | wc -l)"
echo "   - Diretórios vazios restantes: $(find ./src -type d -empty | wc -l)"
echo "   - Arquivos temporários na raiz: $(find . -maxdepth 1 -type f \( -name "*.txt" -o -name "*.log" -o -name "*.tmp" \) | wc -l)"
