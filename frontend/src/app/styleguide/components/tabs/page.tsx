"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function TabsShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Tabs</h1>
        <p className="text-muted-foreground mb-8">
          Navegação entre seções com múltiplas abas.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <Tabs defaultValue="account" className="w-full max-w-md">
          <TabsList>
            <TabsTrigger value="account">Account</TabsTrigger>
            <TabsTrigger value="password">Password</TabsTrigger>
          </TabsList>
          <TabsContent value="account">
            <p className="text-sm text-muted-foreground">
              Make changes to your account here.
            </p>
          </TabsContent>
          <TabsContent value="password">
            <p className="text-sm text-muted-foreground">
              Change your password here.
            </p>
          </TabsContent>
        </Tabs>
      </section>

      {/* Multiple Tabs */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Múltiplas Abas</h2>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">$45,231.89</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          <TabsContent value="analytics">
            <p className="text-sm text-muted-foreground">Analytics content here.</p>
          </TabsContent>
          <TabsContent value="reports">
            <p className="text-sm text-muted-foreground">Reports content here.</p>
          </TabsContent>
          <TabsContent value="notifications">
            <p className="text-sm text-muted-foreground">Notifications content here.</p>
          </TabsContent>
        </Tabs>
      </section>

      {/* Period Selector (Chart Context) */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Seletor de Período (Contexto de Gráfico)</h2>
        <Tabs defaultValue="daily" className="w-full">
          <TabsList>
            <TabsTrigger value="daily">Daily</TabsTrigger>
            <TabsTrigger value="weekly">Weekly</TabsTrigger>
            <TabsTrigger value="monthly">Monthly</TabsTrigger>
          </TabsList>
          <TabsContent value="daily">
            <Card>
              <CardHeader>
                <CardTitle>Daily Report</CardTitle>
                <CardDescription>Performance for the last 24 hours</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Chart data here...</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="weekly">
            <Card>
              <CardHeader>
                <CardTitle>Weekly Report</CardTitle>
                <CardDescription>Performance for the last 7 days</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Chart data here...</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="monthly">
            <Card>
              <CardHeader>
                <CardTitle>Monthly Report</CardTitle>
                <CardDescription>Performance for the last 30 days</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Chart data here...</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    Account settings content
  </TabsContent>
  <TabsContent value="password">
    Password settings content
  </TabsContent>
</Tabs>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Componentes</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Componente</th>
                  <th className="text-left p-2">Props Principais</th>
                  <th className="text-left p-2">Descrição</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">Tabs</td>
                  <td className="p-2 text-sm">defaultValue, value, onValueChange</td>
                  <td className="p-2 text-sm">Container principal controlado/não-controlado</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TabsList</td>
                  <td className="p-2 text-sm">className</td>
                  <td className="p-2 text-sm">Container das tabs (triggers)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TabsTrigger</td>
                  <td className="p-2 text-sm">value, disabled</td>
                  <td className="p-2 text-sm">Botão de aba individual</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TabsContent</td>
                  <td className="p-2 text-sm">value</td>
                  <td className="p-2 text-sm">Conteúdo da aba</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Controlado vs Não-Controlado</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Não-controlado (useState interno) */}
<Tabs defaultValue="tab1">
  {/* ... */}
</Tabs>

{/* Controlado (estado externo) */}
const [activeTab, setActiveTab] = useState("tab1")
<Tabs value={activeTab} onValueChange={setActiveTab}>
  {/* ... */}
</Tabs>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Navegação via setas ← → entre tabs</li>
            <li>Tab/Shift+Tab para entrar/sair da lista de tabs</li>
            <li>Space/Enter para ativar uma tab</li>
            <li>ARIA roles: tablist, tab, tabpanel automaticamente aplicados</li>
            <li>Tab ativa tem aria-selected="true"</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
