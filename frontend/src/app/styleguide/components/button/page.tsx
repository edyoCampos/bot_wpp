"use client"

import { Button } from "@/components/ui/button"
import {
  Mail,
  Loader2,
  ChevronRight,
  Download,
  Plus,
  Trash2
} from "lucide-react"

export default function ButtonShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Button</h1>
        <p className="text-muted-foreground mb-8">
          Componente de ação único com múltiplas variantes, tamanhos e estados.
        </p>
      </div>

      {/* Variants */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Variantes de Tipo</h2>
        <div className="flex flex-wrap gap-4">
          <Button variant="default">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
          <Button variant="destructive">Destructive</Button>
        </div>
      </section>

      {/* Sizes */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Tamanhos</h2>
        <div className="flex flex-wrap items-center gap-4">
          <Button size="sm">Small</Button>
          <Button size="default">Default</Button>
          <Button size="lg">Large</Button>
        </div>
      </section>

      {/* With Icons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Ícones</h2>
        <div className="flex flex-wrap gap-4">
          <Button>
            <Mail />
            Login with Email
          </Button>
          <Button variant="secondary">
            Download
            <Download />
          </Button>
          <Button variant="outline">
            <Plus />
            Add Item
          </Button>
          <Button variant="destructive">
            <Trash2 />
            Delete
          </Button>
        </div>
      </section>

      {/* Icon Only */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Apenas Ícone</h2>
        <div className="flex flex-wrap gap-4">
          <Button size="icon">
            <ChevronRight />
          </Button>
          <Button size="icon-sm" variant="outline">
            <Plus />
          </Button>
          <Button size="icon-lg" variant="secondary">
            <Download />
          </Button>
        </div>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <div className="flex flex-wrap gap-4">
          <Button>Default</Button>
          <Button disabled>Disabled</Button>
          <Button disabled>
            <Loader2 className="animate-spin" />
            Loading
          </Button>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Button } from "@/components/ui/button"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Button>Click me</Button>
<Button variant="secondary">Secondary Action</Button>
<Button variant="outline" size="sm">Small Outline</Button>

{/* Com ícone */}
<Button>
  <Mail />
  Send Email
</Button>

{/* Apenas ícone */}
<Button size="icon">
  <Plus />
</Button>`}</code>
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
                  <td className="p-2 text-sm">"default" | "secondary" | "outline" | "ghost" | "link" | "destructive"</td>
                  <td className="p-2 text-sm">"default"</td>
                  <td className="p-2 text-sm">Estilo visual do botão</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">size</td>
                  <td className="p-2 text-sm">"sm" | "default" | "lg" | "icon" | "icon-sm" | "icon-lg"</td>
                  <td className="p-2 text-sm">"default"</td>
                  <td className="p-2 text-sm">Tamanho do botão</td>
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

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Botões icon-only devem ter aria-label descritivo</li>
            <li>Estado disabled previne interação via teclado e mouse</li>
            <li>Focus ring visível para navegação por teclado</li>
            <li>Suporta navegação via Tab e ativação via Enter/Space</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
