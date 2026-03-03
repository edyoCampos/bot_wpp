"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const datasets = {
  semana: [60, 30, 50, 20, 35, 25, 45],
  mes: [40, 20, 55, 35, 25, 60, 30, 45, 50, 30, 40, 35],
  ano: [50, 45, 55, 35, 40, 60, 50, 65, 45, 55, 50, 60],
}

function pointsToPolyline(points: number[]) {
  const step = 200 / (points.length - 1)
  return points.map((p, i) => `${i * step},${p}`).join(" ")
}

export default function LineChartShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Line Chart</h1>
        <p className="text-muted-foreground mb-8">Gráfico de linhas com períodos.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Performance</CardTitle>
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
                <svg viewBox="0 0 200 80" className="w-full h-48">
                  <polyline
                    fill="none"
                    stroke="hsl(var(--primary))"
                    strokeWidth="2"
                    points={pointsToPolyline(datasets[key])}
                  />
                </svg>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
