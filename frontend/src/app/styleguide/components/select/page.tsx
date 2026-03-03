"use client"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  SelectGroup,
  SelectLabel,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"

export default function SelectShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Select</h1>
        <p className="text-muted-foreground mb-8">
          Seleção de opções em formulários e filtros.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <div className="max-w-sm">
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select a fruit" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="apple">Apple</SelectItem>
              <SelectItem value="banana">Banana</SelectItem>
              <SelectItem value="orange">Orange</SelectItem>
              <SelectItem value="grape">Grape</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </section>

      {/* With Label */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Label</h2>
        <div className="max-w-sm space-y-4">
          <div className="space-y-2">
            <Label htmlFor="framework">Framework</Label>
            <Select>
              <SelectTrigger id="framework">
                <SelectValue placeholder="Select a framework" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="next">Next.js</SelectItem>
                <SelectItem value="react">React</SelectItem>
                <SelectItem value="vue">Vue</SelectItem>
                <SelectItem value="svelte">Svelte</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select defaultValue="active">
              <SelectTrigger id="status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </section>

      {/* With Groups */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Grupos</h2>
        <div className="max-w-sm">
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select a timezone" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>North America</SelectLabel>
                <SelectItem value="est">Eastern Standard Time (EST)</SelectItem>
                <SelectItem value="cst">Central Standard Time (CST)</SelectItem>
                <SelectItem value="mst">Mountain Standard Time (MST)</SelectItem>
                <SelectItem value="pst">Pacific Standard Time (PST)</SelectItem>
              </SelectGroup>
              <SelectGroup>
                <SelectLabel>Europe</SelectLabel>
                <SelectItem value="gmt">Greenwich Mean Time (GMT)</SelectItem>
                <SelectItem value="cet">Central European Time (CET)</SelectItem>
              </SelectGroup>
              <SelectGroup>
                <SelectLabel>Asia</SelectLabel>
                <SelectItem value="jst">Japan Standard Time (JST)</SelectItem>
                <SelectItem value="ist">India Standard Time (IST)</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </section>

      {/* In Forms */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Em Formulários</h2>
        <div className="max-w-md rounded-lg border p-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select defaultValue="medium">
              <SelectTrigger id="priority">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="assignee">Assignee</Label>
            <Select>
              <SelectTrigger id="assignee">
                <SelectValue placeholder="Select team member" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="john">John Doe</SelectItem>
                <SelectItem value="jane">Jane Smith</SelectItem>
                <SelectItem value="bob">Bob Johnson</SelectItem>
                <SelectItem value="alice">Alice Brown</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select>
              <SelectTrigger id="category">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Development</SelectLabel>
                  <SelectItem value="frontend">Frontend</SelectItem>
                  <SelectItem value="backend">Backend</SelectItem>
                  <SelectItem value="devops">DevOps</SelectItem>
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Design</SelectLabel>
                  <SelectItem value="ui">UI Design</SelectItem>
                  <SelectItem value="ux">UX Research</SelectItem>
                </SelectGroup>
                <SelectGroup>
                  <SelectLabel>Marketing</SelectLabel>
                  <SelectItem value="content">Content</SelectItem>
                  <SelectItem value="social">Social Media</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <div className="max-w-sm space-y-4">
          <div className="space-y-2">
            <Label>Default</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select an option" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="option1">Option 1</SelectItem>
                <SelectItem value="option2">Option 2</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Disabled</Label>
            <Select disabled>
              <SelectTrigger>
                <SelectValue placeholder="Disabled select" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="option1">Option 1</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select an option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
    <SelectItem value="option3">Option 3</SelectItem>
  </SelectContent>
</Select>

{/* Com label */}
<div className="space-y-2">
  <Label htmlFor="status">Status</Label>
  <Select defaultValue="active">
    <SelectTrigger id="status">
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="active">Active</SelectItem>
      <SelectItem value="inactive">Inactive</SelectItem>
    </SelectContent>
  </Select>
</div>

{/* Com grupos */}
<SelectContent>
  <SelectGroup>
    <SelectLabel>Group 1</SelectLabel>
    <SelectItem value="a">Item A</SelectItem>
    <SelectItem value="b">Item B</SelectItem>
  </SelectGroup>
  <SelectGroup>
    <SelectLabel>Group 2</SelectLabel>
    <SelectItem value="c">Item C</SelectItem>
  </SelectGroup>
</SelectContent>`}</code>
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
                  <td className="p-2 font-mono text-sm">Select</td>
                  <td className="p-2 text-sm">value, defaultValue, onValueChange, disabled</td>
                  <td className="p-2 text-sm">Container principal (controlado/não-controlado)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">SelectTrigger</td>
                  <td className="p-2 text-sm">className, disabled</td>
                  <td className="p-2 text-sm">Botão que abre o select</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">SelectValue</td>
                  <td className="p-2 text-sm">placeholder</td>
                  <td className="p-2 text-sm">Mostra valor selecionado ou placeholder</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">SelectItem</td>
                  <td className="p-2 text-sm">value, disabled</td>
                  <td className="p-2 text-sm">Opção selecionável</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Controlado vs Não-Controlado</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Não-controlado */}
<Select defaultValue="option1">
  {/* ... */}
</Select>

{/* Controlado */}
const [value, setValue] = useState("")
<Select value={value} onValueChange={setValue}>
  {/* ... */}
</Select>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Sempre associe com Label usando id/htmlFor</li>
            <li>Navegação via setas ↑ ↓</li>
            <li>Typeahead: digite para encontrar opção</li>
            <li>Enter/Space para selecionar</li>
            <li>Esc para fechar sem selecionar</li>
            <li>Suporta required, disabled, aria-invalid</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
