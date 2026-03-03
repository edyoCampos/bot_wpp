"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

export default function DashboardGridShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Dashboard Grid</h1>
        <p className="text-muted-foreground mb-8">
          Grade de dashboard 3 colunas: Kanban 339px, Chart 719px, Projects 340px.
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estrutura</h2>
        <div className="rounded-lg border p-4">
          <div
            className="grid gap-4"
            style={{
              gridTemplateColumns: "339px 719px 340px",
            }}
          >
            {/* Kanban */}
            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Kanban</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div key={i} className="rounded-md border bg-muted/30 p-3 text-sm">
                        Tarefa #{i + 1}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-48 grid grid-cols-6 items-end gap-2">
                    {[30, 60, 90, 50, 70, 40].map((h, i) => (
                      <div key={i} className="bg-primary/70" style={{ height: h }} />
                    ))}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Conversion</CardTitle>
                </CardHeader>
                <CardContent>
                  <svg viewBox="0 0 200 80" className="w-full h-40">
                    <polyline
                      fill="none"
                      stroke="hsl(var(--primary))"
                      strokeWidth="2"
                      points="0,60 40,30 80,50 120,20 160,35 200,25"
                    />
                  </svg>
                </CardContent>
              </Card>
            </div>

            {/* Projects */}
            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Projects</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-sm">Projeto {i + 1}</span>
                        <span className="rounded bg-muted px-2 py-1 text-xs">Ativo</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <p className="text-sm text-muted-foreground">
            Defina colunas fixas com `gridTemplateColumns`. Use `gap` para espaçamento.
          </p>
          <Separator />
          <p className="text-sm text-muted-foreground">
            Este layout espelha a proporção do dashboard descrita no inventário.
          </p>
        </div>
      </section>
    </div>
  )
}
