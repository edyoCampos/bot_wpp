"use client"

import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, ArrowUpDown } from "lucide-react"

const projects = [
  { id: 1, name: "Design System", client: "Acme Corp", status: "In Progress", priority: "High", completion: 75 },
  { id: 2, name: "Mobile App", client: "TechStart", status: "Completed", priority: "Medium", completion: 100 },
  { id: 3, name: "Website Redesign", client: "StartupXYZ", status: "In Progress", priority: "High", completion: 45 },
  { id: 4, name: "API Integration", client: "DevCo", status: "Pending", priority: "Low", completion: 10 },
  { id: 5, name: "Marketing Campaign", client: "BrandCo", status: "In Progress", priority: "Medium", completion: 60 },
]

export default function TableShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Table</h1>
        <p className="text-muted-foreground mb-8">
          Família de componentes de tabela com suporte a sorting, seleção e paginação.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <div className="rounded-lg border">
          <Table>
            <TableCaption>Lista de projetos recentes</TableCaption>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Completion</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.slice(0, 3).map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-medium">{project.name}</TableCell>
                  <TableCell>{project.client}</TableCell>
                  <TableCell>{project.status}</TableCell>
                  <TableCell className="text-right">{project.completion}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* With Selection */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Seleção</h2>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox />
                </TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Completion</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell>
                    <Checkbox />
                  </TableCell>
                  <TableCell className="font-medium">{project.name}</TableCell>
                  <TableCell>{project.client}</TableCell>
                  <TableCell>{project.status}</TableCell>
                  <TableCell className="text-right">{project.completion}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* With Badges and Actions */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Badges e Ações</h2>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Projeto</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Prioridade</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-medium">{project.name}</TableCell>
                  <TableCell>{project.client}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        project.status === "Completed"
                          ? "default"
                          : project.status === "In Progress"
                            ? "secondary"
                            : "outline"
                      }
                      className={
                        project.status === "Completed"
                          ? "bg-green-500"
                          : project.status === "In Progress"
                            ? "bg-blue-500"
                            : ""
                      }
                    >
                      {project.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        project.priority === "High"
                          ? "border-red-500 text-red-600"
                          : project.priority === "Medium"
                            ? "border-yellow-500 text-yellow-600"
                            : "border-gray-500 text-gray-600"
                      }
                    >
                      {project.priority}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon-sm">
                      <MoreHorizontal className="size-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* Sortable Headers */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Headers Sortable</h2>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <Button variant="ghost" size="sm" className="h-8 -ml-3">
                    Nome
                    <ArrowUpDown className="ml-2 size-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button variant="ghost" size="sm" className="h-8 -ml-3">
                    Cliente
                    <ArrowUpDown className="ml-2 size-4" />
                  </Button>
                </TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">
                  <Button variant="ghost" size="sm" className="h-8 -mr-3">
                    Completion
                    <ArrowUpDown className="ml-2 size-4" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.slice(0, 4).map((project) => (
                <TableRow key={project.id}>
                  <TableCell className="font-medium">{project.name}</TableCell>
                  <TableCell>{project.client}</TableCell>
                  <TableCell>{project.status}</TableCell>
                  <TableCell className="text-right">{project.completion}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* Compact Density */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Densidade Compacta</h2>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="h-8">Nome</TableHead>
                <TableHead className="h-8">Cliente</TableHead>
                <TableHead className="h-8">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.slice(0, 5).map((project) => (
                <TableRow key={project.id} className="h-10">
                  <TableCell className="py-2 font-medium">{project.name}</TableCell>
                  <TableCell className="py-2">{project.client}</TableCell>
                  <TableCell className="py-2">{project.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Table>
  <TableCaption>Lista de projetos</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead>Nome</TableHead>
      <TableHead>Status</TableHead>
      <TableHead className="text-right">Valor</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">Projeto 1</TableCell>
      <TableCell>Ativo</TableCell>
      <TableCell className="text-right">$250.00</TableCell>
    </TableRow>
  </TableBody>
</Table>

{/* Com seleção */}
<TableRow>
  <TableCell>
    <Checkbox />
  </TableCell>
  <TableCell>Data</TableCell>
</TableRow>

{/* Headers sortable */}
<TableHead>
  <Button variant="ghost" size="sm">
    Nome
    <ArrowUpDown className="ml-2 size-4" />
  </Button>
</TableHead>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Componentes</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Componente</th>
                  <th className="text-left p-2">Descrição</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">Table</td>
                  <td className="p-2 text-sm">Container principal</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TableCaption</td>
                  <td className="p-2 text-sm">Caption/descrição da tabela</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TableHeader</td>
                  <td className="p-2 text-sm">Container do cabeçalho (thead)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TableBody</td>
                  <td className="p-2 text-sm">Container do corpo (tbody)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TableRow</td>
                  <td className="p-2 text-sm">Linha da tabela (tr)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TableHead</td>
                  <td className="p-2 text-sm">Célula do cabeçalho (th)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">TableCell</td>
                  <td className="p-2 text-sm">Célula de dados (td)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Features</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><strong>Sortable:</strong> Use Button variant="ghost" em TableHead com ícone ArrowUpDown</li>
            <li><strong>Selectable:</strong> Adicione Checkbox na primeira coluna</li>
            <li><strong>Density:</strong> Ajuste altura via className (h-8 header, h-10 rows para compact)</li>
            <li><strong>Responsive:</strong> Envolva em div com overflow-x-auto para scroll horizontal</li>
          </ul>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Usa elementos semânticos table, thead, tbody, tr, th, td</li>
            <li>TableCaption fornece descrição para screen readers</li>
            <li>TableHead usa scope="col" automaticamente</li>
            <li>Para headers sortable, use aria-sort="ascending|descending|none"</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
