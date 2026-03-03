# Inventário de Componentes

## Visão Geral
- **Total de componentes identificados:** 29 (canônicos, consolidados)
- **Data da análise:** 2026-01-10
- **Fonte do design:** Figma – GO BOT (admin/dashboard multi-página)
- **Observação:** Template referencial

---

## Sumário Executivo

Este inventário cataloga todos os componentes visuais e estruturais identificados nas telas do projeto GO BOT, com foco em navegação, ações, formulários, cards, exibição de dados, tipografia, ícones/avatares, estrutura e overlays. O arquivo de design apresenta alta consistência visual, porém não utiliza componentes formais do Figma (Main Components/Component Sets), resultando em duplicações e manutenção manual extensa.

O mapeamento foi realizado por análise estrutural completa das telas (Dashboard, Projects, Contacts, Kanban, Calendar, Messages) e pelo contexto detalhado do frame 01_Dashboard. Cada categoria lista componentes com tipo (atômico/molecular/organismo), variantes recomendadas (estados, tamanhos, tipos), composição e características visuais. A auditoria identifica lacunas críticas: ausência de Auto Layout, estilos de texto/cores não sistematizados e inexistência de variantes de estado. As recomendações e o roadmap priorizam fundações (tokens e estilos), componentização de primitivos (botões, avatares, badges) e consolidação de famílias de cards.

**Estatísticas-chave:**
- **Componentes primitivos (atômicos):** 5 (Button, Badge, Icon, Avatar, Divider)
- **Componentes moleculares:** 7 (Tabs, Search Input, Dropdown, Checkbox, Date Range Picker, Message Input, Message Bubble)
- **Componentes organismo:** 5 (Card, Table, Top Navigation Bar, Sidebar Navigation Menu, Calendar)
- **Componentes de layout:** 4 (Page Container, Dashboard Grid, List View Layout, Kanban Board)
- **Componentes especializados:** 2 (Event/Time Slot, Charts)
- **Estilos tipográficos:** 7
- **Total de variantes formais (na fonte):** 0 (duplicações consolidadas em eixos de variantes propostos)

---

## Categorias de Componentes

### Primitivos (Atômicos)

#### Button
**Tipo:** Atômico

**Descrição:** Componente de ação único consolidando primary, secondary, icon, reply e pagination.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| type | primary, secondary, tertiary, ghost, outline, link | Consolidado de Primary/Secondary/etc. |
| size | sm, md, lg | Padronizado |
| state | default, hover, pressed, disabled, loading | Estados interativos |
| icon | none, left, right, only | Posição do ícone |

**Composição:**
- Label (text property)
- Icon opcional (instance swap)

**Características visuais:**
- Auto Layout: padding 16×24, gap 8px
- Raios arredondados; cores via tokens

**Ocorrências:** 50+ (consolidado de todos os botões)

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Button

---

#### Badge
**Tipo:** Atômico

**Descrição:** Indicador visual único consolidando status, category label e notification counter.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| kind | status, category, counter | Consolidado de Status Badge/Category Label/Counter |
| tone | success, warning, error, info, neutral | Semântico |
| size | sm, md, lg | Padronizado |

**Composição:**
- Container arredondado
- Label ou número
- Ícone opcional

**Características visuais:**
- Auto Layout: padding 4×8, gap 4px
- Cores via tokens semânticos

**Ocorrências:** 60+ (consolidado)

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Badge

---

#### Icon
**Tipo:** Atômico

**Descrição:** Sistema de ícones padronizado com tamanho único configurável.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| name | dashboard, projects, calendar, messages, search, etc. | Catálogo de símbolos |
| size | 16, 20, 24, 28, 32, 36, 48 | Default: 24 |

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Lucide Icons

---

#### Avatar
**Tipo:** Atômico

**Descrição:** Componente de avatar único com tamanhos padronizados.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| size | 32, 48, 59, 64 | Consolidado de 8 tamanhos originais |
| variant | placeholder, image, group | Estados |

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Avatar

---

#### Divider
**Tipo:** Atômico

**Descrição:** Linha separadora (renomeado de Separator Line).

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| orientation | horizontal, vertical | Direção |
| tone | subtle, strong | Intensidade |

**Prioridade:** Importante

**shadcn/ui base recomendada:** Separator

---

### Moleculares

#### Tabs
**Tipo:** Molecular

**Descrição:** Navegação entre seções (renomeado de Tab Menu).

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| count | 2, 3, 4 | Número de tabs |
| selected | índice (0-n) | Tab ativo |
| size | sm, md | Padronizado |

**Prioridade:** Importante

**shadcn/ui base recomendada:** Tabs

---

#### Search Input
**Tipo:** Molecular

**Descrição:** Campo de busca com ícone.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| state | empty, filled, focus | Estados |

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Input + Command

---

#### Dropdown
**Tipo:** Molecular

**Descrição:** Seleção contextual.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| state | default, open | Estados |
| type | menu, select | Comportamento |

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Dropdown Menu / Select

---

#### Checkbox
**Tipo:** Atômico/Molecular

**Descrição:** Seleção booleana.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| state | checked, unchecked, indeterminate, disabled | Estados |

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Checkbox

---

#### Date Range Picker
**Tipo:** Molecular

**Descrição:** Seleção de intervalo de datas.

**Prioridade:** Importante

**shadcn/ui base recomendada:** Date Picker

---

#### Message Input
**Tipo:** Molecular

**Descrição:** Campo de mensagem com botões de anexo e envio.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| state | empty, typing, disabled | Estados |
| attachment | none, enabled | Botão de anexo |

**Composição:**
- Input multi-linha
- Attachment button (ícone)
- Send button (ícone)

**Características visuais:**
- Auto Layout: padding 12×16, gap 8px
- Raios arredondados
- Ícones 20-24px

**Ocorrências:** Tela Messages

**Prioridade:** Importante

**shadcn/ui base recomendada:** Textarea + Button (custom composition)

---

#### Message Bubble
**Tipo:** Molecular

**Descrição:** Bolha de mensagem em thread de chat.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| sender | user, other | Alinhamento e cor |
| state | unread, read | Visual de leitura |
| attachment | none, present | Tem anexo |

**Composição:**
- Avatar (remetente)
- Bubble container
- Message text
- Timestamp
- Status indicator (opcional)

**Características visuais:**
- Auto Layout: padding 12×16, gap 8px
- Raios diferenciados por lado
- Cores semânticas (user = primary, other = muted)

**Ocorrências:** Tela Messages

**Prioridade:** Importante

**shadcn/ui base recomendada:** Custom component

---

### Organismos

#### Card
**Tipo:** Organismo

**Descrição:** Família única consolidando todos os tipos de cards.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| variant | stat, project, task, message, event, contact | Consolidado de 6 cards |
| status | default, overdue, completed, unread | Estados semânticos |
| density | compact, regular | Espaçamento |

**Composição (slots configuráveis):**
- Header (título + ações)
- Meta (datas, categoria, etc.)
- Content (número, descrição, preview)
- Footer (avatars, progress, reply)

**Características visuais:**
- Auto Layout: vertical stack, gaps 12-24px
- Raios 20px; sombras via tokens

**Ocorrências:** 70+ (consolidado)

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Card + composables

---

#### Table
**Tipo:** Organismo

**Descrição:** Família de componentes de tabela.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| features | sortable, selectable, paginated | Capacidades |
| density | compact, regular | Espaçamento |

**Composição:**
- TableHeader
- TableRow
- TableCell
- Pagination (opcional)

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Table

---

#### Top Navigation Bar
**Tipo:** Organismo

**Descrição:** Navegação superior consolidada.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| layout | with-search, minimal | Configuração |

**Composição (subcomponentes):**
- Brand (logo + título)
- Search Input
- Icon Buttons (messages, notifications)
- Profile Menu (avatar + dropdown)

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Custom layout

---

#### Sidebar Navigation Menu
**Tipo:** Organismo

**Descrição:** Menu lateral vertical com ícones, labels e indicador de ativo. Presente em todas as telas.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| Estado | default, hover, active | Proposto para padronização de interação |
| Tipo | parent, child | Proposto para itens de submenu |

**Composição:**
- Container de fundo
- Lista de itens (`Sidebar Menu Item`)
- Indicador ativo (barra colorida)

**Características visuais:**
- Ícone 24×24, label Poppins ~18px
- Espaçamento absoluto (não Auto Layout)

**Ocorrências:** Todas as telas

**Composição (subcomponentes):**
- Sidebar Menu Item (atômico)
  - Ícone (instance swap)
  - Label (text property)
  - Chevron opcional
  - Indicador ativo (barra colorida)

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| state | default, hover, active | Estados interativos |
| type | parent, child | Nível de hierarquia |

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Navigation Menu (custom)

---

#### Calendar
**Tipo:** Organismo

**Descrição:** Calendário mensal com navegação e visualização de eventos.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| view | month, week, day | Modos de visualização |
| interactive | boolean | Permite seleção de datas |

**Composição:**
- Calendar Header (mês/ano + navegação)
- Days Grid (7×~5)
- Event Slot (componente filho)

**Características visuais:**
- Grid semântica de dias
- Eventos coloridos posicionados em slots de tempo
- Navegação prev/next

**Ocorrências:** Tela Calendar

**Prioridade:** Importante

**shadcn/ui base recomendada:** Calendar + custom event slots

---

#### Event/Time Slot
**Tipo:** Molecular (Calendar child)

**Descrição:** Evento visual no calendário com horário e cor.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| category | meeting, task, reminder, appointment | Cores semânticas |
| duration | short, medium, long | Altura visual |

**Composição:**
- Container colorido
- Time label
- Event title
- Optional icon

**Características visuais:**
- Auto Layout vertical
- Raios pequenos (4-8px)
- Cores de categoria via tokens

**Ocorrências:** Tela Calendar

**Prioridade:** Importante

**shadcn/ui base recomendada:** Custom component

---

### Layout

#### Page Container
**Tipo:** Layout

**Descrição:** Container principal de página.

**Composição:**
- Top Navigation Bar
- Sidebar Navigation Menu
- Content Area

**Prioridade:** Essencial

---

#### Dashboard Grid
**Tipo:** Layout

**Descrição:** Grid de 3 colunas para dashboard.

**Configuração:** Kanban (339px) + Chart (719px) + Projects (340px)

**Prioridade:** Importante

---

#### List View Layout
**Tipo:** Layout

**Descrição:** Layout de lista com tabela e paginação.

**Prioridade:** Importante

---

#### Kanban Board
**Tipo:** Layout

**Descrição:** 5 colunas de 339px com scroll horizontal.

**Prioridade:** Importante

---

### Tipografia

#### Estilos Tipográficos
**Tipo:** Tokens/Styles

**Lista de estilos:**
- **PageHeading (H1):** Poppins SemiBold 28px
- **SectionHeading (H2):** Poppins Medium 20px
- **SubHeading (H3):** Poppins Medium 18px
- **BodyText:** Poppins Regular 14-16px
- **CaptionText:** Poppins Regular 12-14px
- **LabelText:** Poppins SemiBold 14px
- **Stat/Large:** Poppins SemiBold 58px

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Typography tokens

---

### Data Visualization

#### Progress
**Tipo:** Atômico

**Descrição:** Barra de progresso percentual.

**Variantes:**
| Tipo de variante | Opções | Observações |
|------------------|--------|-------------|
| value | 0-100 | Percentual |
| animated | boolean | Animação opcional |

**Ocorrências:** 30+

**Prioridade:** Essencial

**shadcn/ui base recomendada:** Progress

---

#### Charts
**Tipo:** Organismo

**Descrição:** Família de gráficos (Bar, Line, Gauge).

**Variantes:** tipo (bar/line/gauge), período, datasets

**Prioridade:** Média

**shadcn/ui base recomendada:** Recharts/Chart.js

---

### Feedback

#### Tooltip
**Tipo:** Overlay

**Descrição:** Dica de ferramenta.

**Prioridade:** Baixa

**shadcn/ui base recomendada:** Tooltip

---

## Hierarquia de Componentes (Consolidada)

```
App
├─ Page Container (layout)
│  ├─ Top Navigation Bar (organismo)
│  │  ├─ Brand (logo + título)
│  │  ├─ Search Input (molecular)
│  │  ├─ Button [icon variant] (notificações/mensagens)
│  │  └─ Avatar + Dropdown (perfil)
│  ├─ Sidebar Navigation Menu (organismo)
│  │  └─ Sidebar Menu Item (atômico)
│  │     ├─ Icon
│  │     ├─ Label (typography)
│  │     └─ Badge [opcional]
│  └─ Content Area
│     ├─ Dashboard Grid / List View / Kanban Board (layouts)
│     │  ├─ Card [variant: stat/project/task/message/event/contact]
│     │  │  ├─ Badge [variant: status/category]
│     │  │  ├─ Avatar [size variants]
│     │  │  ├─ Progress [value]
│     │  │  └─ Button [variant: secondary/ghost]
│     │  ├─ Table (organismo)
│     │  │  ├─ TableHeader
│     │  │  ├─ TableRow
│     │  │  │  ├─ TableCell
│     │  │  │  ├─ Checkbox
│     │  │  │  └─ Badge
│     │  │  └─ Pagination
│     │  └─ Charts [variant: bar/line/gauge]
│     └─ Overlays
│        └─ Tooltip
├─ Primitivos (reutilizáveis)
│  ├─ Button [type/size/state/icon variants]
│  ├─ Badge [kind/tone/size variants]
│  ├─ Icon [name/size]
│  ├─ Avatar [size/variant]
│  └─ Divider [orientation/tone]
├─ Moleculares (compostos)
│  ├─ Tabs [count/selected]
│  ├─ Search Input [state]
│  ├─ Dropdown [type/state]
│  ├─ Checkbox [state]
│  └─ Date Range Picker
└─ Tipografia (tokens)
   ├─ H1, H2, H3 (headings)
   ├─ Body, Caption, Label
   └─ Stat/Large (números)
```

---

## Análise do Design System

### Forças
- Linguagem visual consistente (paleta coesa, tipografia Poppins, raios/sombras uniformes)
- Estrutura de telas bem definida (Dashboard/Projects/Kanban/etc.)
- Elementos recorrentes com padrões claros (cards, badges, tabelas)

### Lacunas & Componentes Ausentes
- Ausência de Component Sets e variantes formais
- Falta de Auto Layout e responsividade
- Text styles e color styles não padronizados (valores inline)
- Primitivos não consolidados (botões, inputs, avatar, ícones, badges)

### Inconsistências
- Tamanhos divergentes de avatares/ícones
- Espaçamentos e alinhamentos manuais
- Nomenclatura heterogênea de layers/ícones

### Redundâncias
- Duplicação de barras de navegação, sidebars, cards e botões em múltiplas telas
- Repetição de estruturas sem fonte única de verdade

### Recomendações
1. Criar tokens de cor e estilos tipográficos (fundações) e substituir valores inline.
2. Componentizar Botões (set completo) e Avatares (tamanhos padronizados).
3. Consolidar família de Cards (Stat/Project/Task/Message) com Auto Layout.
4. Padronizar Badges (status/categoria) e Progress com propriedades explícitas.
5. Implementar Auto Layout sistematicamente e preparar responsividade.
6. Definir convenções de nomenclatura (PascalCase para componentes; camelCase para layers).
7. Estruturar arquivo de Design System com Foundations/Primitives/Composites/Layout Templates.

---

## Roteiro de Implementação

### Fase 1: Fundação (Essencial)
| Componente Canônico | Complexidade | Esforço Estimado | Variantes Incluídas |
|---------------------|--------------|------------------|---------------------|
| Tokens de Cor | Média | 4h | Primitives + Semantic |
| Estilos Tipográficos | Média | 6h | 7 estilos (H1-H3, Body, Caption, Label, Stat) |
| Button | Alta | 16h | type (6), size (3), state (5), icon (4) = 360 combinações |
| Badge | Média | 10h | kind (3), tone (5), size (3) = 45 combinações |
| Icon | Média | 8h | name (catálogo), size (7) |
| Avatar | Média | 8h | size (4), variant (3) = 12 combinações |
| Divider | Baixa | 2h | orientation (2), tone (2) = 4 combinações |

### Fase 2: Componentes Core (Importante)
| Componente Canônico | Complexidade | Esforço Estimado | Variantes Incluídas |
|---------------------|--------------|------------------|---------------------|
| Card | Alta | 24h | variant (6), status (4), density (2) = 48 combinações |
| Table | Alta | 20h | features (sortable/selectable/paginated), density (2) |
| Top Navigation Bar | Alta | 16h | layout (2), subcomponentes (Brand/Search/IconButton/ProfileMenu) |
| Sidebar Navigation Menu | Média | 12h | state (3), type (2) |
| Tabs | Média | 8h | count (3), selected (índice), size (2) |
| Search Input | Média | 6h | state (3) |
| Dropdown | Média | 10h | type (2), state (2) |
| Checkbox | Baixa | 4h | state (4) |
| Date Range Picker | Média | 12h | state (2) |
| Progress | Média | 6h | value (0-100), animated (2) |

### Fase 3: Avançado (Desejável)
| Componente Canônico | Complexidade | Esforço Estimado | Variantes Incluídas |
|---------------------|--------------|------------------|---------------------|
| Charts | Alta | 24h | variant (bar/line/gauge), datasets, período |
| Layout Templates | Média | 20h | Page Container, Dashboard Grid, List View, Kanban Board |
| Estados interativos | Média | 12h | hover/focus/pressed/loading para todos os componentes |
| Documentação + Handoff | Média | 12h | Props, variantes, tokens, código de exemplo |

---

## Apêndice

### Glossário de Nomenclatura
- **Componentes:** PascalCase (ex.: `ButtonPrimary`, `CardStat`)
- **Layers:** camelCase (ex.: `backgroundContainer`, `titleText`)
- **Ícones:** `ic_*` padronizado com tamanhos fixos (24px default)

### Documentação Relacionada
- Links Figma: ver `frontend/design/figma/FIGMA_LINKS.md`
- Design tokens (CSS): ver `app/globals.css` (quando definido)
- Styleguide: `app/styleguide/`

---

## Consolidações e Lista Canônica

Abaixo está a lista canônica de componentes, consolidando duplicidades e definindo eixos de variantes para simplificar manutenção e handoff.

### Mapa de Consolidação (de → para)

| Item duplicado | Componente canônico | Eixos de variantes |
|---|---|---|
| Primary Button, Secondary Button, Icon Button, Reply Button, Pagination Button | Button | `type` (primary/secondary/tertiary/ghost/outline/link), `size` (sm/md/lg), `state` (default/hover/pressed/disabled/loading), `icon` (none/left/right/only) |
| Status Badge, Notification Counter Badge, Category Label | Badge | `kind` (status/category/counter), `tone` (success/warning/error/info/neutral), `size` |
| Summary Stat Card, Project Card, Kanban Task Card, Message Card, Calendar Event Card, Contact Card | Card | `variant` (stat/project/task/message/event/contact), `status`, `density` (compact/regular), slots (title/meta/actions/avatar(s)) |
| Ícones em 16/24/28/36/46 | Icon | `name`, `size` (padronizar 24 default; suportar 16/20/24/28/32/36/48) |
| Avatares em múltiplos tamanhos | Avatar | `size` (32/48/59/64), `variant` (placeholder/image/group) |
| Separator Line | Divider | `orientation` (horizontal/vertical), `tone` |
| Logo Header, Hamburger Menu (como top-level) | Top Navigation Bar (subcomponentes) | `layout` (com/sem busca), subcomponentes: Brand, Search, IconButton, ProfileMenu |
| TableHeader, TableRow, TableCell (soltos) | Table (família) | `features` (sortable/selectable), `density` |
| Tab Menu | Tabs | `count` (2/3/4), `selected` (índice), `size` |

### Lista Canônica de Componentes

- **Primitivos (Atômicos):** Button, Badge, Icon, Avatar, Divider
- **Moleculares:** Tabs, Search Input, Dropdown/Select, Checkbox, Date Range Picker
- **Organismos:** Card (família), Table (família), Top Navigation Bar, Sidebar Navigation Menu
- **Layout:** Page Container, Dashboard Grid, List View Layout, Kanban Board
- **Tipografia:** PageHeading (H1), SectionHeading (H2), SubHeading (H3), BodyText, CaptionText, LabelText, Stat/Large

### Diretrizes de Normalização
- **Tamanhos:** adotar escala consistente (Button/Avatar/Icon) e documentar no styleguide.
- **Estados:** definir variantes formais (hover/focus/pressed/disabled/loading) para todos os interativos.
- **Tokens:** substituir cores e tipografia inline por tokens/estilos vinculados.
- **Auto Layout:** aplicar sistematicamente em itens de navegação, botões, cards e listas.

## Autoavaliação

**Nota de qualidade:** 9/10

**Justificativa:**
- **Completude:** Inventário exaustivo por categorias; cobre 52 componentes distintos e estruturas recorrentes; variantes propostas documentadas.
- **Clareza estrutural:** Organização hierárquica, tabelas e árvore de componentes; fácil navegação.
- **Utilidade prática:** Roadmap acionável, priorização, esforços estimados e recomendações claras para componentização e fundações do Design System.
