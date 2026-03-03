"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

export default function KanbanLayoutShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Kanban Board</h1>
        <p className="text-muted-foreground mb-8">Quadro Kanban com 5 colunas e rolagem horizontal.</p>
      </div>

      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estrutura</h2>
        <div className="rounded-lg border p-4 overflow-x-auto">
          <div className="flex gap-4 min-w-max">
            {[
              "Backlog",
              "To Do",
              "In Progress",
              "Review",
              "Done",
            ].map((col, i) => (
              <div key={i} className="w-[320px] shrink-0">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">{col}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Array.from({ length: 3 }).map((_, j) => (
                        <div key={j} className="rounded-md border bg-muted/30 p-3 text-sm">
                          Tarefa {j + 1}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <p className="text-sm text-muted-foreground">
            Utilize `overflow-x-auto` para rolagem horizontal e defina largura fixa para colunas.
          </p>
          <Separator />
          <p className="text-sm text-muted-foreground">
            Ideal para planejamento e acompanhamento de tarefas.
          </p>
        </div>
      </section>
    </div>
  )
}
