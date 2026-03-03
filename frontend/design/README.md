z# Design System - Go

Documentação e recursos de design do projeto.

## Estrutura

```
design/
├── figma/          # Arquivos e links do Figma
├── assets/         # Assets exportados (ícones, ilustrações)
└── README.md       # Este arquivo
```

## Figma

### Links

Adicione aqui os links para os arquivos do Figma:

- **Design System**: [Link para o Figma]
- **Protótipos**: [Link para o Figma]
- **Componentes**: [Link para o Figma]

### Arquivos

Coloque em `figma/` arquivos como:
- `.fig` - Arquivos do Figma (se exportados)
- Design tokens (JSON/CSS)
- Exports de estilos
- Documentação de componentes

## Assets

Em `assets/` mantenha:
- Ícones exportados (SVG)
- Ilustrações
- Imagens de mockups
- Logos em diferentes formatos

## Design Tokens

Se usar design tokens do Figma, considere integrá-los com Tailwind CSS:

```javascript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        // Tokens do Figma
      }
    }
  }
}
```

## Workflow

1. Design no Figma
2. Exportar componentes/assets necessários
3. Integrar com shadcn/ui quando possível
4. Manter documentação atualizada
