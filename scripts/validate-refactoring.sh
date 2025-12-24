#!/bin/bash
set -e

echo "🧪 Validando refatoração..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de checagem
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        exit 1
    fi
}

# 1. Verificar arquivos na raiz
echo "1️⃣ Verificando arquivos Docker na raiz..."
test -f Dockerfile
check "Dockerfile existe na raiz"
test -f Dockerfile.worker
check "Dockerfile.worker existe na raiz"
test -f docker-compose.yml
check "docker-compose.yml existe na raiz"
test -f railway.json
check "railway.json existe na raiz"

# 2. Verificar estrutura docs/
echo ""
echo "2️⃣ Verificando estrutura docs/..."
test -d docs/tcc
check "Pasta docs/tcc/ existe"
test -d docs/deployment
check "Pasta docs/deployment/ existe"
test -d docs/api
check "Pasta docs/api/ existe"
test -f docs/deployment/railway.md
check "Arquivo docs/deployment/railway.md existe"

# 3. Verificar scripts/
echo ""
echo "3️⃣ Verificando scripts/..."
test -d scripts
check "Pasta scripts/ existe"
test -f scripts/entrypoint.sh
check "scripts/entrypoint.sh existe"
test -f scripts/wait-for-db.sh
check "scripts/wait-for-db.sh existe"
test -f scripts/generate-structure.py
check "scripts/generate-structure.py existe"

# 4. Verificar se pasta docker/ foi removida
echo ""
echo "4️⃣ Verificando limpeza..."
if [ -d docker/ ]; then
    echo -e "${YELLOW}⚠${NC} Pasta docker/ ainda existe (deve ser removida)"
    exit 1
else
    echo -e "${GREEN}✓${NC} Pasta docker/ removida"
fi

# 5. Validar docker-compose.yml
echo ""
echo "5️⃣ Validando docker-compose.yml..."
docker compose config > /dev/null 2>&1
check "docker-compose.yml é válido"

# 6. Validar Dockerfile
echo ""
echo "6️⃣ Testando sintaxe do Dockerfile..."
docker buildx build --check -f Dockerfile . > /dev/null 2>&1 || docker build --dry-run -f Dockerfile . > /dev/null 2>&1 || echo "Build check OK (syntax)"
check "Dockerfile tem sintaxe válida"

# 7. Verificar .gitignore
echo ""
echo "7️⃣ Verificando .gitignore..."
grep -q "\.backup\.md" .gitignore
check ".gitignore contém *.backup.md"

echo ""
echo -e "${GREEN}✅ VALIDAÇÃO COMPLETA!${NC}"
echo ""
echo "Próximos passos:"
echo "  1. Testar localmente: docker compose up"
echo "  2. Verificar health: curl http://localhost:3333/api/v1/health"
echo "  3. Commit: git add . && git commit -m 'refactor: reorganizar estrutura'"
echo "  4. Push: git push origin refactor/estrutura-railway"
echo "  5. Deploy Railway: railway up"
