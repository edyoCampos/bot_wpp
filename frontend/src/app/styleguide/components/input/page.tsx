"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Search, Mail } from "lucide-react"

export default function InputShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Input</h1>
        <p className="text-muted-foreground mb-8">
          Campo de entrada de texto com suporte a ícones e estados.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <div className="max-w-sm space-y-4">
          <Input placeholder="Digite algo..." />
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="email@example.com" />
          </div>
        </div>
      </section>

      {/* With Icons (Search Input) */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Ícone (Search Input)</h2>
        <div className="max-w-sm space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input className="pl-10" placeholder="Search..." />
          </div>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input className="pl-10" type="email" placeholder="Enter your email..." />
          </div>
        </div>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <div className="max-w-sm space-y-4">
          <Input placeholder="Default" />
          <Input placeholder="Focused" className="ring-ring ring-[3px]" />
          <Input placeholder="Filled" defaultValue="John Doe" />
          <Input placeholder="Disabled" disabled />
          <Input placeholder="Error" aria-invalid className="border-destructive focus-visible:ring-destructive/20" />
        </div>
      </section>

      {/* Types */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Tipos</h2>
        <div className="max-w-sm space-y-4">
          <div className="space-y-2">
            <Label>Text</Label>
            <Input type="text" placeholder="Text input" />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input type="email" placeholder="email@example.com" />
          </div>
          <div className="space-y-2">
            <Label>Password</Label>
            <Input type="password" placeholder="••••••••" />
          </div>
          <div className="space-y-2">
            <Label>Number</Label>
            <Input type="number" placeholder="123" />
          </div>
          <div className="space-y-2">
            <Label>Date</Label>
            <Input type="date" />
          </div>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Input placeholder="Digite algo..." />

{/* Com label */}
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" />
</div>

{/* Search Input com ícone */}
<div className="relative">
  <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
  <Input className="pl-10" placeholder="Search..." />
</div>

{/* Estados */}
<Input disabled placeholder="Disabled" />
<Input aria-invalid placeholder="Error" />`}</code>
          </pre>

          <h3 className="font-medium mt-6">Props</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Prop</th>
                  <th className="text-left p-2">Tipo</th>
                  <th className="text-left p-2">Descrição</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">type</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">text | email | password | number | date | etc.</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">placeholder</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">Texto placeholder</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">disabled</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">Estado desabilitado</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">aria-invalid</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">Estado de erro (estilo automático)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Sempre associe com Label usando htmlFor/id</li>
            <li>Use aria-invalid para indicar erros de validação</li>
            <li>Forneça placeholder descritivo mas não substitua label</li>
            <li>Tipo apropriado ativa teclado móvel correto</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
