"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const datasets = {
  semana: [30, 60, 90, 50, 70, 40, 65],
  mes: [45, 75, 55, 80, 60, 95, 70, 50, 85, 40, 65, 90],
  ano: [60, 70, 65, 80, 75, 90, 85, 95, 70, 60, 75, 85],
}

export default function BarChartShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Bar Chart</h1>
        <p className="text-muted-foreground mb-8">Gráfico de barras com períodos.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Conversões</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="semana" className="space-y-4">
            <TabsList>
              <TabsTrigger value="semana">Semana</TabsTrigger>
              <TabsTrigger value="mes">Mês</TabsTrigger>
              <TabsTrigger value="ano">Ano</TabsTrigger>
            </TabsList>
            {(Object.keys(datasets) as Array<keyof typeof datasets>).map((key) => (
              <TabsContent key={key} value={key}>
                <div className="h-48 grid items-end gap-2" style={{ gridTemplateColumns: `repeat(${datasets[key].length}, 1fr)` }}>
                  {datasets[key].map((h, i) => (
                    <div key={i} className="bg-primary/70" style={{ height: h }} />
                  ))}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
