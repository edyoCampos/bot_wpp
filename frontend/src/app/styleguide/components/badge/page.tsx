"use client"

import { Badge } from "@/components/ui/badge"
import { Check, X, AlertCircle, Info } from "lucide-react"

export default function BadgeShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Badge</h1>
        <p className="text-muted-foreground mb-8">
          Indicador visual único consolidando status, category label e notification counter.
        </p>
      </div>

      {/* Variants */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Variantes</h2>
        <div className="flex flex-wrap gap-4">
          <Badge variant="default">Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="outline">Outline</Badge>
          <Badge variant="destructive">Destructive</Badge>
        </div>
      </section>

      {/* Status Badges */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Status (Semântico)</h2>
        <div className="flex flex-wrap gap-4">
          <Badge variant="default" className="bg-success text-success-foreground hover:bg-success/90">
            <Check />
            Success
          </Badge>
          <Badge variant="default" className="bg-warning text-warning-foreground hover:bg-warning/90">
            <AlertCircle />
            Warning
          </Badge>
          <Badge variant="destructive">
            <X />
            Error
          </Badge>
          <Badge variant="default" className="bg-info text-info-foreground hover:bg-info/90">
            <Info />
            Info
          </Badge>
          <Badge variant="secondary">Neutral</Badge>
        </div>
      </section>

      {/* Category Labels */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Categorias</h2>
        <div className="flex flex-wrap gap-4">
          <Badge variant="outline" className="border-success text-success-foreground">
            Design
          </Badge>
          <Badge variant="outline" className="border-info text-info-foreground">
            Development
          </Badge>
          <Badge variant="outline" className="border-warning text-warning-foreground">
            Marketing
          </Badge>
          <Badge variant="outline" className="border-success text-success-foreground">
            Sales
          </Badge>
        </div>
      </section>

      {/* Counters */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Contadores</h2>
        <div className="flex flex-wrap gap-4">
          <Badge variant="destructive">3</Badge>
          <Badge variant="default">12</Badge>
          <Badge variant="secondary">99+</Badge>
        </div>
      </section>

      {/* With Icons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Ícones</h2>
        <div className="flex flex-wrap gap-4">
          <Badge variant="default">
            <Check />
            Completed
          </Badge>
          <Badge variant="secondary">
            <AlertCircle />
            Pending
          </Badge>
          <Badge variant="destructive">
            <X />
            Cancelled
          </Badge>
        </div>
      </section>

      {/* Sizes (via className) */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Tamanhos</h2>
        <div className="flex flex-wrap items-center gap-4">
          <Badge className="text-[10px] px-1.5 py-0">Small</Badge>
          <Badge>Medium (default)</Badge>
          <Badge className="text-sm px-3 py-1">Large</Badge>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Badge } from "@/components/ui/badge"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="outline">Outline</Badge>
<Badge variant="destructive">Error</Badge>

{/* Status semântico */}
<Badge className="bg-green-500">
  <Check />
  Approved
</Badge>

{/* Contador */}
<Badge variant="destructive">5</Badge>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Props</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Prop</th>
                  <th className="text-left p-2">Tipo</th>
                  <th className="text-left p-2">Padrão</th>
                  <th className="text-left p-2">Descrição</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">variant</td>
                  <td className="p-2 text-sm">"default" | "secondary" | "outline" | "destructive"</td>
                  <td className="p-2 text-sm">"default"</td>
                  <td className="p-2 text-sm">Estilo visual do badge</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">asChild</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Renderiza como filho (Radix Slot)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Customização de Cores</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Tons semânticos via className */}
<Badge className="bg-success text-success-foreground">Success</Badge>
<Badge className="bg-warning text-warning-foreground">Warning</Badge>
<Badge className="bg-info text-info-foreground">Info</Badge>

{/* Categorias com outline */}
<Badge variant="outline" className="border-success text-success-foreground">
  Design
</Badge>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Badges puramente decorativos não precisam de role/aria-label</li>
            <li>Para badges com significado semântico, considere aria-label</li>
            <li>Contadores devem ter contexto (ex: "3 mensagens não lidas")</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
