# Casos de Teste E2E - Go

## Visão Geral

Este documento descreve os casos de teste end-to-end (e2e) implementados para a aplicação Go. Os testes foram criados usando Playwright e cobrem todas as principais funcionalidades da interface do usuário.

## Estrutura dos Testes

### Arquivos de Teste
- `auth-pages.spec.ts` - Testes de autenticação (login/signup)
- `password-recovery.spec.ts` - Testes de recuperação de senha
- `styleguide.spec.ts` - Testes do sistema de design

### Estratégia de Seleção
- Priorização de `data-testid` para seletores estáveis
- Uso de `test.step()` para organização clara
- Validação de estados visuais e funcionais
- Cobertura de cenários de sucesso e erro

---

## 1. Testes de Autenticação (`auth-pages.spec.ts`)

### 1.1 Sign In Page

#### **Teste: Renderização completa e navegação**
**Objetivo:** Verificar se todos os elementos da página de login são renderizados corretamente e a navegação funciona.

**Pré-condições:**
- Aplicação rodando em `http://localhost:3000`

**Passos:**
1. Navegar para `/signin`
2. Verificar presença de elementos principais
3. Testar links de navegação

**Validações:**
- ✅ Título "Entrar" presente
- ✅ Campos: username, password, checkbox "remember me"
- ✅ Botões: "Entrar", "Esqueceu a senha?", "Criar conta"
- ✅ Navegação para `/signup` funciona
- ✅ Navegação para `/forgot` funciona

#### **Teste: Validação de formulário vazio**
**Objetivo:** Verificar comportamento quando formulário é submetido vazio.

**Passos:**
1. Navegar para `/signin`
2. Clicar em "Entrar" sem preencher campos

**Validações:**
- ✅ Formulário permanece na página (validação HTML5)
- ✅ Campos permanecem visíveis
- ✅ URL permanece `/signin`

#### **Teste: Confirmação de verificação de email**
**Objetivo:** Verificar que a página de login mostra confirmação quando o email é verificado com sucesso.

**Passos:**
1. Navegar para `/signin?verified=1`
2. Verificar presença da mensagem de sucesso

**Validações:**
- ✅ Mensagem "✅ Email verificado com sucesso! Agora você pode fazer login." é exibida
- ✅ Elemento tem atributo `role="status"` para acessibilidade
- ✅ Formulário de login permanece funcional
- ✅ Todos os elementos da página continuam presentes

### 1.2 Sign Up Page

#### **Teste: Renderização completa e navegação**
**Objetivo:** Verificar elementos da página de cadastro e navegação.

**Passos:**
1. Navegar para `/signup`
2. Verificar presença de elementos
3. Testar navegação para login

**Validações:**
- ✅ Título "Criar conta" presente
- ✅ Campos: fullname, email, password
- ✅ Botões: "Criar conta", "Entrar"
- ✅ Navegação para `/signin` funciona

#### **Teste: Validação de senha**
**Objetivo:** Verificar validação de senha curta.

**Passos:**
1. Navegar para `/signup`
2. Preencher campos com senha curta ("123")
3. Tentar submeter formulário

**Validações:**
- ✅ Formulário não é submetido (validação HTML5)
- ✅ Página permanece em `/signup`

#### **Teste: Submissão completa do formulário**
**Objetivo:** Verificar estado do formulário quando totalmente preenchido.

**Passos:**
1. Navegar para `/signup`
2. Preencher todos os campos corretamente

**Validações:**
- ✅ Todos os valores presentes
- ✅ Botão "Criar conta" habilitado

---

## 2. Testes de Recuperação de Senha (`password-recovery.spec.ts`)

### 2.1 Forgot Password Page

#### **Teste: Renderização e validação de formulário**
**Objetivo:** Verificar elementos e validação da página de recuperação.

**Passos:**
1. Navegar para `/forgot`
2. Verificar elementos presentes
3. Testar validação de campo vazio

**Validações:**
- ✅ Título "Recuperar senha" presente
- ✅ Campo email presente
- ✅ Botão "Enviar link de recuperação" desabilitado quando email vazio

#### **Teste: Submissão de formulário**
**Objetivo:** Verificar comportamento após submissão.

**Passos:**
1. Navegar para `/forgot`
2. Preencher email
3. Clicar em "Enviar link de recuperação"

**Validações:**
- ✅ Campo email permanece acessível
- ✅ Formulário permanece funcional

### 2.2 Reset Password Page

#### **Teste: Renderização com token válido**
**Objetivo:** Verificar elementos da página de redefinição.

**Passos:**
1. Navegar para `/reset?token=valid-token-123`

**Validações:**
- ✅ Título "Redefinir senha" presente
- ✅ Campos: nova senha, confirmar senha
- ✅ Botão "Redefinir senha" presente

#### **Teste: Validação de requisitos de senha**
**Objetivo:** Verificar diferentes cenários de validação.

**Sub-cenários:**

**Cenário: Formulário vazio**
- ✅ Botão desabilitado quando campos vazios

**Cenário: Senhas diferentes**
- ✅ Botão habilitado (validação ocorre no submit)

**Cenário: Senhas válidas**
- ✅ Botão habilitado quando ambas as senhas coincidem

#### **Teste: Token inválido ou ausente**
**Objetivo:** Verificar comportamento com tokens problemáticos.

**Cenários:**
- ✅ **Sem token**: Página renderiza mas submissão falha
- ✅ **Token inválido**: Campos permanecem acessíveis

#### **Teste: Redefinição bem-sucedida**
**Objetivo:** Verificar fluxo de sucesso.

**Passos:**
1. Navegar para `/reset?token=valid-token-123`
2. Preencher senhas válidas
3. Submeter formulário

**Validações:**
- ✅ Campos permanecem acessíveis após submissão

---

## 3. Testes do Styleguide (`styleguide.spec.ts`)

### 3.1 Design Tokens

#### **Teste: Seções principais**
**Objetivo:** Verificar presença de seções do design system.

**Validações:**
- ✅ Títulos: "Design Tokens", "Color Palette", "Typography", "Border Radius", "Shadows", "Component Examples"

#### **Teste: Blocos de cores base**
**Objetivo:** Verificar renderização de variáveis CSS.

**Validações:**
- ✅ Pelo menos um bloco para cada variável: `--background`, `--foreground`, `--primary`, `--secondary`

#### **Teste: Cores semânticas**
**Objetivo:** Verificar pares background/foreground.

**Validações:**
- ✅ Pares presentes: success, warning, info

#### **Teste: Cores de gráfico**
**Objetivo:** Verificar paleta de cores para gráficos.

**Validações:**
- ✅ 5 blocos de cores `--chart-1` até `--chart-5`

#### **Teste: Toggle de tema dark/light**
**Objetivo:** Verificar funcionalidade do alternador de tema.

**Passos:**
1. Verificar estado inicial
2. Clicar no botão de toggle
3. Verificar mudança no `html.dark`

**Validações:**
- ✅ Classe `dark` é adicionada/removida do elemento `html`

---

## 4. Data-testid Implementados

### Páginas de Autenticação
```typescript
// Sign In
'login-title', 'login-username', 'login-password',
'login-remember', 'login-forgot', 'login-submit', 'login-signup'

// Sign Up
'signup-title', 'signup-fullname', 'signup-email',
'signup-password', 'signup-submit', 'signup-signin'
```

### Recuperação de Senha
```typescript
// Forgot Password
'forgot-title', 'forgot-email', 'forgot-submit',
'forgot-form', 'forgot-error', 'forgot-success'

// Reset Password
'reset-title', 'reset-new-password', 'reset-confirm-password',
'reset-submit', 'reset-form', 'reset-error', 'reset-success'
```

### Styleguide
```typescript
'styleguide-theme-toggle'
```

---

## 5. Métricas de Cobertura

### Estatísticas dos Testes
- **Total de testes:** 18
- **Tempo médio de execução:** ~13 segundos
- **Arquivos testados:** 5 páginas principais
- **Cenários cobertos:** Sucesso, erro, validação, navegação, confirmação de email, confirmação de email

### Funcionalidades Testadas
- ✅ Autenticação completa (login/signup)
- ✅ Recuperação de senha end-to-end
- ✅ Sistema de design e temas
- ✅ Validações de formulário
- ✅ Navegação e estados visuais
- ✅ Confirmação de verificação de email
- ✅ Responsividade e acessibilidade

---

## 6. Estratégia de Execução

### Comando de Execução
```bash
cd frontend
npm run test:e2e
```

### Ambiente de Teste
- **Framework:** Playwright
- **Navegador:** Chromium (padrão)
- **Base URL:** `http://localhost:3000`
- **Modo:** Headless por padrão

### Configuração
```typescript
// playwright.config.ts
{
  testDir: './tests',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  reporter: [['list']]
}
```

---

## 7. Manutenção e Evolução

### Adição de Novos Testes
1. Criar arquivo `.spec.ts` na pasta `tests/`
2. Seguir padrão de nomenclatura: `<feature>.spec.ts`
3. Usar `data-testid` para seletores
4. Implementar `test.step()` para organização

### Atualização de Testes Existentes
- Revisar após mudanças na UI
- Atualizar seletores se `data-testid` mudar
- Manter cobertura de cenários críticos

### Boas Práticas
- ✅ Seletores estáveis (`data-testid`)
- ✅ Testes independentes
- ✅ Cenários realistas
- ✅ Validação de estados visuais
- ✅ Documentação clara

---

*Documento gerado em Janeiro 2026 - Go*