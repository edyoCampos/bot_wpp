"use client"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { MoreVertical, Calendar, User } from "lucide-react"

export default function CardShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Card</h1>
        <p className="text-muted-foreground mb-8">
          Família única consolidando todos os tipos de cards com múltiplas variantes.
        </p>
      </div>

      {/* Stat Cards */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Stat Cards (Métricas)</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
              <User className="size-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">245</div>
              <p className="text-xs text-muted-foreground">+12% from last month</p>
            </CardContent>
          </Card>
          <Card className="bg-primary text-primary-foreground">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
              <Calendar className="size-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234</div>
              <p className="text-xs opacity-80">+8% from last week</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">573</div>
              <p className="text-xs text-muted-foreground">+20.1% from last month</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Messages</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">89</div>
              <p className="text-xs text-muted-foreground">3 unread</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Project Cards */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Project Cards</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-base">Design System</CardTitle>
                  <CardDescription>Acme Corp.</CardDescription>
                </div>
                <Button variant="ghost" size="icon-sm">
                  <MoreVertical className="size-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="size-4" />
                <span>Due: Jan 15, 2026</span>
              </div>
              <div className="flex -space-x-2">
                <Avatar className="size-8 border-2 border-background">
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <Avatar className="size-8 border-2 border-background">
                  <AvatarFallback>AB</AvatarFallback>
                </Avatar>
                <Avatar className="size-8 border-2 border-background">
                  <AvatarFallback>+3</AvatarFallback>
                </Avatar>
              </div>
            </CardContent>
          </Card>

          <Card className="border-destructive bg-destructive/5">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-base">Backend API</CardTitle>
                  <CardDescription>TechStart Inc.</CardDescription>
                </div>
                <Badge variant="destructive">Overdue</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-destructive">
                <Calendar className="size-4" />
                <span>Due: Jan 8, 2026</span>
              </div>
              <div className="flex -space-x-2">
                <Avatar className="size-8 border-2 border-background">
                  <AvatarFallback>MK</AvatarFallback>
                </Avatar>
              </div>
            </CardContent>
          </Card>

          <Card className="border-green-500 bg-green-50 dark:bg-green-950/20">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-base">Mobile App</CardTitle>
                  <CardDescription>StartupXYZ</CardDescription>
                </div>
                <Badge className="bg-green-500">Completed</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="size-4" />
                <span>Completed: Jan 5, 2026</span>
              </div>
              <div className="flex -space-x-2">
                <Avatar className="size-8 border-2 border-background">
                  <AvatarFallback>PL</AvatarFallback>
                </Avatar>
                <Avatar className="size-8 border-2 border-background">
                  <AvatarFallback>TR</AvatarFallback>
                </Avatar>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Task Cards (Kanban) */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Task Cards (Kanban)</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <Badge variant="outline" className="w-fit border-purple-500 text-purple-600">Design</Badge>
              <CardTitle className="text-base mt-2">Create wireframes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span>75%</span>
                </div>
                <Progress value={75} />
              </div>
              <div className="flex -space-x-2">
                <Avatar className="size-6 border-2 border-background">
                  <AvatarFallback className="text-xs">JD</AvatarFallback>
                </Avatar>
                <Avatar className="size-6 border-2 border-background">
                  <AvatarFallback className="text-xs">AB</AvatarFallback>
                </Avatar>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <Badge variant="outline" className="w-fit border-blue-500 text-blue-600">Development</Badge>
              <CardTitle className="text-base mt-2">Implement API endpoints</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span>45%</span>
                </div>
                <Progress value={45} />
              </div>
              <div className="flex -space-x-2">
                <Avatar className="size-6 border-2 border-background">
                  <AvatarFallback className="text-xs">MK</AvatarFallback>
                </Avatar>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <Badge variant="outline" className="w-fit border-orange-500 text-orange-600">Marketing</Badge>
              <CardTitle className="text-base mt-2">Launch campaign</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span>90%</span>
                </div>
                <Progress value={90} />
              </div>
              <div className="flex -space-x-2">
                <Avatar className="size-6 border-2 border-background">
                  <AvatarFallback className="text-xs">PL</AvatarFallback>
                </Avatar>
                <Avatar className="size-6 border-2 border-background">
                  <AvatarFallback className="text-xs">TR</AvatarFallback>
                </Avatar>
                <Avatar className="size-6 border-2 border-background">
                  <AvatarFallback className="text-xs">XY</AvatarFallback>
                </Avatar>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Message Cards */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Message Cards</h2>
        <div className="max-w-2xl space-y-3">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-start gap-3">
                <Avatar>
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">John Doe</CardTitle>
                    <span className="text-xs text-muted-foreground">2h ago</span>
                  </div>
                  <CardDescription className="text-sm">
                    Hey, can you review the latest design mockups?
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardFooter className="pt-0">
              <Button variant="outline" size="sm">Reply</Button>
            </CardFooter>
          </Card>

          <Card className="bg-muted/50">
            <CardHeader className="pb-3">
              <div className="flex items-start gap-3">
                <Avatar>
                  <AvatarFallback>AB</AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-sm">Alice Brown</CardTitle>
                      <Badge variant="default" className="bg-blue-500">Unread</Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">15m ago</span>
                  </div>
                  <CardDescription className="text-sm font-medium text-foreground">
                    Meeting scheduled for tomorrow at 10 AM
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardFooter className="pt-0">
              <Button variant="outline" size="sm">Reply</Button>
            </CardFooter>
          </Card>
        </div>
      </section>

      {/* Density Variants */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Densidade</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Compact</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">Less padding for dense layouts</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Regular</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">Standard padding for comfortable reading</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content goes here
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

{/* Stat Card */}
<Card>
  <CardHeader className="flex flex-row items-center justify-between pb-2">
    <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
    <DollarSign className="size-4 text-muted-foreground" />
  </CardHeader>
  <CardContent>
    <div className="text-2xl font-bold">$45,231</div>
    <p className="text-xs text-muted-foreground">+20.1% from last month</p>
  </CardContent>
</Card>

{/* Project Card com status */}
<Card className="border-destructive bg-destructive/5">
  <CardHeader>
    <div className="flex items-start justify-between">
      <CardTitle>Project Name</CardTitle>
      <Badge variant="destructive">Overdue</Badge>
    </div>
  </CardHeader>
  {/* ... */}
</Card>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Variantes Consolidadas</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Variante</th>
                  <th className="text-left p-2">Uso</th>
                  <th className="text-left p-2">Classes</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">stat</td>
                  <td className="p-2 text-sm">Métricas com número grande</td>
                  <td className="p-2 text-sm">CardHeader com flex-row, CardTitle text-sm</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">project</td>
                  <td className="p-2 text-sm">Projetos com datas e avatares</td>
                  <td className="p-2 text-sm">Status via className (border-destructive, etc.)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">task</td>
                  <td className="p-2 text-sm">Tarefas com categoria e progress</td>
                  <td className="p-2 text-sm">Badge + Progress components</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">message</td>
                  <td className="p-2 text-sm">Mensagens com avatar e reply</td>
                  <td className="p-2 text-sm">Avatar + Button em CardFooter</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Estados Semânticos</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Overdue */}
<Card className="border-destructive bg-destructive/5">

{/* Completed */}
<Card className="border-green-500 bg-green-50 dark:bg-green-950/20">

{/* Unread */}
<Card className="bg-muted/50">`}</code>
          </pre>

          <h3 className="font-medium mt-6">Componentes Slots</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><code className="bg-muted px-1">CardHeader</code> - Cabeçalho com título e descrição</li>
            <li><code className="bg-muted px-1">CardTitle</code> - Título do card (h3 por padrão)</li>
            <li><code className="bg-muted px-1">CardDescription</code> - Subtítulo/descrição</li>
            <li><code className="bg-muted px-1">CardContent</code> - Conteúdo principal</li>
            <li><code className="bg-muted px-1">CardFooter</code> - Footer com ações</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
