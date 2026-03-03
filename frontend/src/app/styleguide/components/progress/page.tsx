"use client"

import { Progress } from "@/components/ui/progress"
import { useEffect, useState } from "react"

export default function ProgressShowcase() {
  const [progress, setProgress] = useState(13)

  useEffect(() => {
    const timer = setTimeout(() => setProgress(66), 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Progress</h1>
        <p className="text-muted-foreground mb-8">
          Barra de progresso percentual com animação.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <div className="max-w-md space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>0%</span>
              <span className="text-muted-foreground">Progress</span>
            </div>
            <Progress value={0} />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>33%</span>
              <span className="text-muted-foreground">Progress</span>
            </div>
            <Progress value={33} />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>66%</span>
              <span className="text-muted-foreground">Progress</span>
            </div>
            <Progress value={66} />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>100%</span>
              <span className="text-muted-foreground">Completo</span>
            </div>
            <Progress value={100} />
          </div>
        </div>
      </section>

      {/* Animated */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Animado</h2>
        <div className="max-w-md space-y-2">
          <div className="flex justify-between text-sm">
            <span>{progress}%</span>
            <span className="text-muted-foreground">Carregando...</span>
          </div>
          <Progress value={progress} />
        </div>
      </section>

      {/* In Card Context */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Em Cards (Contexto de Tarefa)</h2>
        <div className="grid gap-4 md:grid-cols-2 max-w-2xl">
          <div className="rounded-lg border p-4 space-y-3">
            <div>
              <h3 className="font-medium">Design System</h3>
              <p className="text-sm text-muted-foreground">UI Components</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progresso</span>
                <span>75%</span>
              </div>
              <Progress value={75} />
            </div>
          </div>
          <div className="rounded-lg border p-4 space-y-3">
            <div>
              <h3 className="font-medium">Backend API</h3>
              <p className="text-sm text-muted-foreground">Development</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progresso</span>
                <span>45%</span>
              </div>
              <Progress value={45} />
            </div>
          </div>
          <div className="rounded-lg border p-4 space-y-3">
            <div>
              <h3 className="font-medium">Documentation</h3>
              <p className="text-sm text-muted-foreground">Content</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progresso</span>
                <span>90%</span>
              </div>
              <Progress value={90} />
            </div>
          </div>
          <div className="rounded-lg border p-4 space-y-3">
            <div>
              <h3 className="font-medium">Testing</h3>
              <p className="text-sm text-muted-foreground">QA</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progresso</span>
                <span>20%</span>
              </div>
              <Progress value={20} />
            </div>
          </div>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Progress } from "@/components/ui/progress"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Progress value={33} />
<Progress value={66} />
<Progress value={100} />

{/* Com label */}
<div className="space-y-2">
  <div className="flex justify-between text-sm">
    <span>{progress}%</span>
    <span className="text-muted-foreground">Progresso</span>
  </div>
  <Progress value={progress} />
</div>

{/* Animado */}
const [progress, setProgress] = useState(0)
useEffect(() => {
  const timer = setInterval(() => {
    setProgress((prev) => Math.min(prev + 10, 100))
  }, 500)
  return () => clearInterval(timer)
}, [])
<Progress value={progress} />`}</code>
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
                  <td className="p-2 font-mono text-sm">value</td>
                  <td className="p-2 text-sm">number</td>
                  <td className="p-2 text-sm">0</td>
                  <td className="p-2 text-sm">Valor de 0 a 100</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">max</td>
                  <td className="p-2 text-sm">number</td>
                  <td className="p-2 text-sm">100</td>
                  <td className="p-2 text-sm">Valor máximo</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Usa role="progressbar" automaticamente</li>
            <li>aria-valuemin, aria-valuemax, aria-valuenow são aplicados</li>
            <li>Para progresso indeterminado, omita value (mostra estado de loading)</li>
            <li>Animação transition-all suaviza mudanças de valor</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
