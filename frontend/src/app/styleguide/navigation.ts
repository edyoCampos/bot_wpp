export interface NavItem {
  name: string
  href: string
}

export interface NavSection {
  title: string
  items: NavItem[]
}

export const navigation: NavSection[] = [
  {
    title: "Foundation",
    items: [
      { name: "Design Tokens", href: "/styleguide" },
    ]
  },
  {
    title: "Components",
    items: [
      { name: "Avatar", href: "/styleguide/components/avatar" },
      { name: "Badge", href: "/styleguide/components/badge" },
      { name: "Button", href: "/styleguide/components/button" },
      { name: "Calendar", href: "/styleguide/components/calendar" },
      { name: "Card", href: "/styleguide/components/card" },
      { name: "Checkbox", href: "/styleguide/components/checkbox" },
      { name: "Contact Card", href: "/styleguide/components/contact-card" },
      { name: "Dropdown Menu", href: "/styleguide/components/dropdown-menu" },
      { name: "Input", href: "/styleguide/components/input" },
      { name: "Login Form", href: "/styleguide/components/login-form" },
      { name: "Message Bubble", href: "/styleguide/components/message-bubble" },
      { name: "Message Input", href: "/styleguide/components/message-input" },
      { name: "Progress", href: "/styleguide/components/progress" },
      { name: "Select", href: "/styleguide/components/select" },
      { name: "Separator", href: "/styleguide/components/separator" },
      { name: "Table", href: "/styleguide/components/table" },
      { name: "Tabs", href: "/styleguide/components/tabs" },
      { name: "Tooltip", href: "/styleguide/components/tooltip" },
    ]
  },
  {
    title: "Layouts",
    items: [
      { name: "Page Container", href: "/styleguide/components/layouts/page-container" },
      { name: "Dashboard Grid", href: "/styleguide/components/layouts/dashboard-grid" },
      { name: "List View", href: "/styleguide/components/layouts/list-view" },
      { name: "Kanban", href: "/styleguide/components/layouts/kanban" },
    ]
  },
  {
    title: "Charts",
    items: [
      { name: "Bar", href: "/styleguide/components/charts/bar" },
      { name: "Line", href: "/styleguide/components/charts/line" },
      { name: "Gauge", href: "/styleguide/components/charts/gauge" },
    ]
  }
]
