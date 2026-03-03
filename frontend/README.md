# Frontend - Go

Frontend desenvolvido com **Next.js** seguindo a documentação oficial.

## Stack

- **Framework**: Next.js 16.1.1
- **React**: 19.2.3
- **TypeScript**: 5.x
- **Estilização**: Tailwind CSS v4
- **Componentes**: shadcn/ui
- **App Router**: Habilitado (usando `app/` directory)
- **Server Components**: Padrão (Client Components quando necessário)

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── app/              # App Router - páginas e layouts
│   │   ├── layout.tsx    # Layout raiz
│   │   ├── page.tsx      # Página inicial
│   │   └── globals.css   # Estilos globais
│   └── lib/              # Utilitários
│       └── utils.ts      # shadcn/ui utils
├── public/               # Arquivos estáticos
├── components.json       # Configuração shadcn/ui
├── next.config.ts        # Configuração Next.js
├── tailwind.config.ts    # Configuração Tailwind
└── tsconfig.json         # Configuração TypeScript
```

## Como Executar

### Instalação de Dependências

```bash
cd frontend
npm install
```

### Modo Desenvolvimento

```bash
npm run dev
```

O aplicativo estará disponível em: **http://localhost:3000**

### Build de Produção

```bash
npm run build
```

### Iniciar Produção

```bash
npm start
```

### Linting

```bash
npm run lint
```

### Formatação (Prettier)

```bash
# Formatar todos os arquivos
npm run format

# Verificar formatação sem modificar
npm run format:check
```

## Adicionando Componentes shadcn/ui

Para adicionar componentes do shadcn/ui:

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
# etc...
```

Os componentes serão adicionados em `src/components/ui/`

## Convenções

### Server Components vs Client Components

- **Server Components** (padrão): Não requerem diretiva especial
- **Client Components**: Adicionar `"use client"` no topo do arquivo

### Imports Absolutos

Use o alias `@/` para imports:

```typescript
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
```

### Rotas

Seguir a estrutura do App Router:

```
app/
├── page.tsx              # /
├── about/
│   └── page.tsx          # /about
└── dashboard/
    ├── layout.tsx        # Layout do dashboard
    └── page.tsx          # /dashboard
```

## Recursos

- [Documentação Next.js](https://nextjs.org/docs)
- [Documentação shadcn/ui](https://ui.shadcn.com)
- [Documentação Tailwind CSS](https://tailwindcss.com/docs)
