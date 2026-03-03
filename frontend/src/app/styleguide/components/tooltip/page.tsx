"use client"

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Button } from "@/components/ui/button"
import { Info, HelpCircle, Plus } from "lucide-react"

export default function TooltipShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Tooltip</h1>
        <p className="text-muted-foreground mb-8">
          Dica de ferramenta para fornecer informações contextuais.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline">Hover me</Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>This is a tooltip</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </section>

      {/* With Icons */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Ícones</h2>
        <TooltipProvider>
          <div className="flex gap-4">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon">
                  <Info />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>More information</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon">
                  <HelpCircle />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Get help</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon">
                  <Plus />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Add new item</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </TooltipProvider>
      </section>

      {/* Positions */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Posições</h2>
        <TooltipProvider>
          <div className="flex gap-4 flex-wrap">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline">Top (default)</Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Tooltip on top</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline">Right</Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Tooltip on right</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline">Bottom</Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <p>Tooltip on bottom</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline">Left</Button>
              </TooltipTrigger>
              <TooltipContent side="left">
                <p>Tooltip on left</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </TooltipProvider>
      </section>

      {/* Rich Content */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Conteúdo Rico</h2>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline">Rich Tooltip</Button>
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">
              <div className="space-y-2">
                <p className="font-medium">Keyboard Shortcut</p>
                <p className="text-sm text-muted-foreground">
                  Press <kbd className="px-1 py-0.5 bg-muted rounded">Cmd</kbd> + <kbd className="px-1 py-0.5 bg-muted rounded">K</kbd> to open command palette
                </p>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </section>

      {/* In Context (Charts) */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Em Contexto (Gráficos)</h2>
        <div className="rounded-lg border p-6">
          <h3 className="font-medium mb-4 flex items-center gap-2">
            Monthly Revenue
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon-sm" className="size-5">
                    <Info className="size-3" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Total revenue from all sources</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </h3>
          <div className="text-3xl font-bold">$45,231.89</div>
          <p className="text-sm text-muted-foreground mt-2">+20.1% from last month</p>
        </div>
      </section>

      {/* Delay Variants */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Variações de Delay</h2>
        <TooltipProvider>
          <div className="flex gap-4">
            <Tooltip delayDuration={0}>
              <TooltipTrigger asChild>
                <Button variant="outline">Instant</Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>No delay (0ms)</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline">Default</Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Default delay (700ms)</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip delayDuration={1000}>
              <TooltipTrigger asChild>
                <Button variant="outline">Slow</Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Slow delay (1000ms)</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </TooltipProvider>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Sempre envolva com TooltipProvider */}
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="outline">Hover me</Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Tooltip text</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>

{/* Com ícone */}
<Tooltip>
  <TooltipTrigger asChild>
    <Button variant="ghost" size="icon">
      <Info />
    </Button>
  </TooltipTrigger>
  <TooltipContent>
    <p>More info</p>
  </TooltipContent>
</Tooltip>

{/* Posicionamento */}
<TooltipContent side="right">
  <p>Right side</p>
</TooltipContent>

{/* Delay customizado */}
<Tooltip delayDuration={0}>
  {/* Instant */}
</Tooltip>`}</code>
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
                  <td className="p-2 font-mono text-sm">TooltipProvider</td>
                  <td className="p-2 text-sm">delayDuration, skipDelayDuration</td>
                  <td className="p-2 text-sm">Provider global (envolve todos os tooltips)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">Tooltip</td>
                  <td className="p-2 text-sm">delayDuration, open, onOpenChange</td>
                  <td className="p-2 text-sm">Container do tooltip individual</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TooltipTrigger</td>
                  <td className="p-2 text-sm">asChild</td>
                  <td className="p-2 text-sm">Elemento que dispara o tooltip</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TooltipContent</td>
                  <td className="p-2 text-sm">side, sideOffset, align</td>
                  <td className="p-2 text-sm">Conteúdo do tooltip</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Posições (side)</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><code className="bg-muted px-1">top</code> - Acima do elemento (padrão)</li>
            <li><code className="bg-muted px-1">right</code> - À direita</li>
            <li><code className="bg-muted px-1">bottom</code> - Abaixo</li>
            <li><code className="bg-muted px-1">left</code> - À esquerda</li>
          </ul>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Não usa focus - apenas hover (considere fornecer info de outra forma para keyboard users)</li>
            <li>Usa role="tooltip" automaticamente</li>
            <li>Fecha ao pressionar Esc</li>
            <li>Para info crítica, use Dialog ou Popover ao invés de Tooltip</li>
            <li>Evite tooltips em elementos touch-only (mobile)</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
