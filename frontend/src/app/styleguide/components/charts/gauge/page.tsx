"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function arcPath(value: number) {
  const clamped = Math.max(0, Math.min(100, value))
  const angle = (clamped / 100) * Math.PI
  const x = 100 + 80 * Math.cos(Math.PI - angle)
  const y = 100 - 80 * Math.sin(Math.PI - angle)
  const largeArc = clamped > 50 ? 1 : 0
  return `M 20 100 A 80 80 0 ${largeArc} 1 ${x} ${y}`
}

export default function GaugeChartShowcase() {
  const value = 68
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Gauge</h1>
        <p className="text-muted-foreground mb-8">Indicador semicircular de progresso.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Nível de Serviço</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full flex justify-center">
            <svg viewBox="0 0 200 120" className="w-full max-w-md">
              <path d="M 20 100 A 80 80 0 1 1 180 100" fill="none" stroke="hsl(var(--muted))" strokeWidth="12" />
              <path d={arcPath(value)} fill="none" stroke="hsl(var(--primary))" strokeWidth="12" />
              <text x="100" y="105" textAnchor="middle" className="fill-foreground" fontSize="18" fontWeight="600">
                {value}%
              </text>
            </svg>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
