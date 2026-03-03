"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"

export default function ListViewLayoutShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">List View Layout</h1>
        <p className="text-muted-foreground mb-8">Layout de lista com tabela e paginação.</p>
      </div>

      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Tabela</h2>
        <Card>
          <CardHeader>
            <CardTitle>Registros</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell>Item {i + 1}</TableCell>
                    <TableCell>Ativo</TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="secondary">Editar</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="mt-4 flex items-center justify-between">
              <div className="text-sm text-muted-foreground">Mostrando 1-5 de 42</div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline">Anterior</Button>
                <Button size="sm">Próximo</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
