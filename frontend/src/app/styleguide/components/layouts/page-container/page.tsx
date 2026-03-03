"use client"

import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Menu, Search, Bell } from "lucide-react"

export default function PageContainerShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Page Container</h1>
        <p className="text-muted-foreground mb-8">
          Container principal de página com Top Navigation, Sidebar e área de conteúdo.
        </p>
      </div>

      {/* Layout */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estrutura</h2>
        <div className="rounded-lg border overflow-hidden">
          {/* Top Navigation */}
          <header className="flex items-center gap-3 border-b p-3 bg-background">
            <Button variant="ghost" size="icon-sm" aria-label="Toggle sidebar">
              <Menu className="size-4" />
            </Button>
            <div className="font-semibold">GO BOT</div>
            <div className="ml-auto flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input className="pl-10 w-[280px]" placeholder="Search..." />
              </div>
              <Button variant="ghost" size="icon-sm" aria-label="Notifications">
                <Bell className="size-4" />
              </Button>
              <Avatar className="size-8">
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
            </div>
          </header>

          <div className="flex">
            {/* Sidebar Navigation */}
            <aside className="w-[240px] border-r p-3 space-y-1">
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent">
                <span className="inline-block size-2 rounded bg-primary" />
                Dashboard
              </button>
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent">
                Projects
              </button>
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent">
                Contacts
              </button>
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent">
                Messages
                <Badge className="ml-auto">3</Badge>
              </button>
              <Separator className="my-2" />
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent">
                Calendar
              </button>
              <button className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent">
                Kanban
              </button>
            </aside>

            {/* Content Area */}
            <main className="flex-1 p-4 space-y-6">
              <Tabs defaultValue="overview">
                <TabsList>
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="analytics">Analytics</TabsTrigger>
                  <TabsTrigger value="reports">Reports</TabsTrigger>
                </TabsList>
                <TabsContent value="overview" className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <Card key={i}>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm">Stat {i + 1}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">1,234</div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>
                <TabsContent value="analytics">
                  <div className="grid gap-4 md:grid-cols-2">
                    <Card>
                      <CardHeader>
                        <CardTitle>Bar Chart</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="h-40 grid grid-cols-6 items-end gap-2">
                          {[30, 60, 90, 50, 70, 40].map((h, i) => (
                            <div key={i} className="bg-primary/70" style={{ height: h }} />
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader>
                        <CardTitle>Line Chart</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <svg viewBox="0 0 200 80" className="w-full h-40">
                          <polyline
                            fill="none"
                            stroke="hsl(var(--primary))"
                            strokeWidth="2"
                            points="0,60 40,30 80,50 120,20 160,35 200,25"
                          />
                        </svg>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
                <TabsContent value="reports">
                  <div className="grid gap-4 md:grid-cols-3">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <Card key={i}>
                        <CardHeader>
                          <CardTitle>Report {i + 1}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground">Summary content...</p>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </main>
          </div>
        </div>
      </section>

      {/* Uso */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <p className="text-sm text-muted-foreground">
            Composição: Top Navigation + Sidebar + Content Area. Utilize CSS Grid/Flex para organizar áreas.
          </p>
        </div>
      </section>
    </div>
  )
}
