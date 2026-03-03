"use client"

import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useState } from "react"

export default function CalendarShowcase() {
  const [date, setDate] = useState<Date | undefined>(new Date())
  const [dates, setDates] = useState<Date[] | undefined>([])

  return (
    <div className="space-y-12 p-8">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Calendar</h1>
        <p className="text-muted-foreground mb-8">
          Calendário mensal com navegação e seleção de datas.
        </p>
      </div>

      {/* Single Date */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Seleção Única</h2>
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <Calendar
              mode="single"
              selected={date}
              onSelect={setDate}
              className="rounded-md border"
            />
            {date && (
              <p className="mt-4 text-sm text-muted-foreground">
                Data selecionada: {date.toLocaleDateString('pt-BR')}
              </p>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Multiple Dates */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Seleção Múltipla</h2>
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <Calendar
              mode="multiple"
              selected={dates}
              onSelect={setDates}
              className="rounded-md border"
            />
            {dates && dates.length > 0 && (
              <p className="mt-4 text-sm text-muted-foreground">
                {dates.length} data(s) selecionada(s)
              </p>
            )}
          </CardContent>
        </Card>
      </section>

      {/* With Events Preview */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Eventos</h2>
        <Card>
          <CardHeader>
            <CardTitle>Setembro 2024</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <Calendar
                mode="single"
                selected={date}
                onSelect={setDate}
                className="rounded-md border"
              />
              <div className="space-y-3">
                <h3 className="font-medium">Eventos do Dia</h3>
                <div className="space-y-2">
                  <div className="p-3 rounded-md bg-blue-50 border-l-4 border-blue-500">
                    <div className="text-sm font-medium">09:00 - 10:00</div>
                    <div className="text-sm">Reunião com cliente</div>
                  </div>
                  <div className="p-3 rounded-md bg-green-50 border-l-4 border-green-500">
                    <div className="text-sm font-medium">14:00 - 15:30</div>
                    <div className="text-sm">Weekly Meeting for Vora App</div>
                  </div>
                  <div className="p-3 rounded-md bg-orange-50 border-l-4 border-orange-500">
                    <div className="text-sm font-medium">19:30 - 20:30</div>
                    <div className="text-sm">Meeting Invoice Designs</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Calendar } from "@/components/ui/calendar"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`const [date, setDate] = useState<Date | undefined>(new Date())

<Calendar
  mode="single"
  selected={date}
  onSelect={setDate}
  className="rounded-md border"
/>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Seleção Múltipla</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`const [dates, setDates] = useState<Date[] | undefined>([])

<Calendar
  mode="multiple"
  selected={dates}
  onSelect={setDates}
  className="rounded-md border"
/>`}</code>
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
                  <td className="p-2 font-mono text-sm">mode</td>
                  <td className="p-2 text-sm">"single" | "multiple" | "range"</td>
                  <td className="p-2 text-sm">Modo de seleção</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">selected</td>
                  <td className="p-2 text-sm">Date | Date[]</td>
                  <td className="p-2 text-sm">Data(s) selecionada(s)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">onSelect</td>
                  <td className="p-2 text-sm">(date) =&gt; void</td>
                  <td className="p-2 text-sm">Callback ao selecionar</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">disabled</td>
                  <td className="p-2 text-sm">Date[] | function</td>
                  <td className="p-2 text-sm">Datas desabilitadas</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Navegação via setas ← → ↑ ↓</li>
            <li>Enter ou Space para selecionar</li>
            <li>PageUp/PageDown para mudar mês</li>
            <li>Home/End para primeira/última semana</li>
            <li>ARIA labels para leitores de tela</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
