"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

export default function CheckboxShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Checkbox</h1>
        <p className="text-muted-foreground mb-8">
          Seleção booleana em tabelas, filtros e formulários.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <div className="space-y-4">
          <Checkbox />
          <div className="flex items-center space-x-2">
            <Checkbox id="terms" />
            <Label htmlFor="terms">Aceito os termos e condições</Label>
          </div>
        </div>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Checkbox id="unchecked" />
            <Label htmlFor="unchecked">Unchecked</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="checked" defaultChecked />
            <Label htmlFor="checked">Checked</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="indeterminate" checked="indeterminate" />
            <Label htmlFor="indeterminate">Indeterminate</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="disabled" disabled />
            <Label htmlFor="disabled" className="text-muted-foreground">Disabled</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="disabled-checked" disabled defaultChecked />
            <Label htmlFor="disabled-checked" className="text-muted-foreground">Disabled + Checked</Label>
          </div>
        </div>
      </section>

      {/* In Forms */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Em Formulários</h2>
        <div className="max-w-md space-y-4 rounded-lg border p-6">
          <div>
            <h3 className="font-medium mb-4">Preferências de Notificação</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox id="email-notifications" defaultChecked />
                <Label htmlFor="email-notifications">Email notifications</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="sms-notifications" />
                <Label htmlFor="sms-notifications">SMS notifications</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="push-notifications" defaultChecked />
                <Label htmlFor="push-notifications">Push notifications</Label>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* In Tables */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Em Tabelas (Seleção Múltipla)</h2>
        <div className="rounded-lg border">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="p-3 text-left w-12">
                  <Checkbox />
                </th>
                <th className="p-3 text-left">Nome</th>
                <th className="p-3 text-left">Email</th>
                <th className="p-3 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="p-3">
                  <Checkbox />
                </td>
                <td className="p-3">John Doe</td>
                <td className="p-3">john@example.com</td>
                <td className="p-3">Active</td>
              </tr>
              <tr className="border-b">
                <td className="p-3">
                  <Checkbox defaultChecked />
                </td>
                <td className="p-3">Jane Smith</td>
                <td className="p-3">jane@example.com</td>
                <td className="p-3">Active</td>
              </tr>
              <tr>
                <td className="p-3">
                  <Checkbox />
                </td>
                <td className="p-3">Bob Johnson</td>
                <td className="p-3">bob@example.com</td>
                <td className="p-3">Inactive</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Com label */}
<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Aceito os termos</Label>
</div>

{/* Estados */}
<Checkbox defaultChecked />
<Checkbox disabled />
<Checkbox checked="indeterminate" />

{/* Controlado */}
const [checked, setChecked] = useState(false)
<Checkbox checked={checked} onCheckedChange={setChecked} />`}</code>
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
                  <td className="p-2 font-mono text-sm">checked</td>
                  <td className="p-2 text-sm">boolean | "indeterminate"</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Estado controlado</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">defaultChecked</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Estado inicial (não-controlado)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">onCheckedChange</td>
                  <td className="p-2 text-sm">(checked) =&gt; void</td>
                  <td className="p-2 text-sm">-</td>
                  <td className="p-2 text-sm">Callback ao mudar estado</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">disabled</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Estado desabilitado</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Sempre associe com Label usando id/htmlFor</li>
            <li>Suporta navegação via Tab</li>
            <li>Ativação via Space</li>
            <li>Estado indeterminate para seleção parcial (ex: "selecionar tudo")</li>
            <li>Usa role="checkbox" e aria-checked automaticamente</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
