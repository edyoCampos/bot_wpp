"use client"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { MoreVertical, User, Settings, LogOut, Check } from "lucide-react"
import { useState } from "react"

export default function DropdownMenuShowcase() {
  const [showStatusBar, setShowStatusBar] = useState(true)
  const [position, setPosition] = useState("bottom")

  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Dropdown Menu</h1>
        <p className="text-muted-foreground mb-8">
          Menu contextual para ações e seleções.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">Open Menu</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Billing</DropdownMenuItem>
            <DropdownMenuItem>Team</DropdownMenuItem>
            <DropdownMenuItem>Subscription</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      {/* With Icons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Ícones</h2>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <User />
              Account
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive">
              <LogOut />
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      {/* With Shortcuts */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Atalhos</h2>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">Editor</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuItem>
              New File
              <DropdownMenuShortcut>⌘N</DropdownMenuShortcut>
            </DropdownMenuItem>
            <DropdownMenuItem>
              Open File
              <DropdownMenuShortcut>⌘O</DropdownMenuShortcut>
            </DropdownMenuItem>
            <DropdownMenuItem>
              Save
              <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              Print
              <DropdownMenuShortcut>⌘P</DropdownMenuShortcut>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      {/* Checkbox Items */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Checkboxes</h2>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">View</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>Appearance</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuCheckboxItem checked={showStatusBar} onCheckedChange={setShowStatusBar}>
              Status Bar
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem checked>
              Activity Bar
            </DropdownMenuCheckboxItem>
            <DropdownMenuCheckboxItem>
              Panel
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      {/* Radio Group */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Radio Group</h2>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">Position: {position}</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>Panel Position</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuRadioGroup value={position} onValueChange={setPosition}>
              <DropdownMenuRadioItem value="top">Top</DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="bottom">Bottom</DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="right">Right</DropdownMenuRadioItem>
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      {/* Context Menu (Icon Trigger) */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Menu de Ações (Icon Trigger)</h2>
        <div className="flex gap-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVertical />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Edit</DropdownMenuItem>
              <DropdownMenuItem>Duplicate</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon-sm">
                <MoreVertical />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>View Details</DropdownMenuItem>
              <DropdownMenuItem>Share</DropdownMenuItem>
              <DropdownMenuItem>Download</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>

{/* Com ícones */}
<DropdownMenuItem>
  <User />
  Profile
</DropdownMenuItem>

{/* Com atalho */}
<DropdownMenuItem>
  Save
  <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
</DropdownMenuItem>

{/* Icon trigger */}
<DropdownMenuTrigger asChild>
  <Button variant="ghost" size="icon">
    <MoreVertical />
  </Button>
</DropdownMenuTrigger>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Componentes Especiais</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Checkbox items */}
<DropdownMenuCheckboxItem checked={value} onCheckedChange={setValue}>
  Option
</DropdownMenuCheckboxItem>

{/* Radio group */}
<DropdownMenuRadioGroup value={value} onValueChange={setValue}>
  <DropdownMenuRadioItem value="option1">Option 1</DropdownMenuRadioItem>
  <DropdownMenuRadioItem value="option2">Option 2</DropdownMenuRadioItem>
</DropdownMenuRadioGroup>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Props Principais</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Componente</th>
                  <th className="text-left p-2">Props</th>
                  <th className="text-left p-2">Descrição</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">DropdownMenuContent</td>
                  <td className="p-2 text-sm">align, sideOffset</td>
                  <td className="p-2 text-sm">Posicionamento do menu</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">DropdownMenuItem</td>
                  <td className="p-2 text-sm">disabled, onSelect</td>
                  <td className="p-2 text-sm">Item de menu clicável</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">DropdownMenuCheckboxItem</td>
                  <td className="p-2 text-sm">checked, onCheckedChange</td>
                  <td className="p-2 text-sm">Item com checkbox</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Navegação via setas ↑ ↓</li>
            <li>Tab/Shift+Tab para entrar/sair</li>
            <li>Enter/Space para selecionar item</li>
            <li>Esc para fechar</li>
            <li>Suporta typeahead (digitar para encontrar item)</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
