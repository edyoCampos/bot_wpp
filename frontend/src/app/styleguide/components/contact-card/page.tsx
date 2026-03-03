"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Phone, Video, MessageSquare, X } from "lucide-react"

interface ContactCardProps {
  name: string
  company: string
  initials: string
  isOnline?: boolean
  isSelected?: boolean
  onSelect?: () => void
}

function ContactCard({
  name,
  company,
  initials,
  isOnline = false,
  isSelected = false,
  onSelect,
}: ContactCardProps) {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${isSelected ? 'ring-2 ring-primary' : ''}`}
      onClick={onSelect}
    >
      <CardContent className="p-6 space-y-4">
        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <Avatar className="size-20">
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>
            {isOnline && (
              <span className="absolute bottom-0 right-0 size-4 rounded-full bg-green-500 border-2 border-white" />
            )}
          </div>

          <div className="text-center">
            <h3 className="font-semibold text-base">{name}</h3>
            <p className="text-sm text-muted-foreground">{company}</p>
          </div>
        </div>

        <div className="flex items-center justify-center gap-2">
          <Button variant="ghost" size="icon-sm" aria-label="Call">
            <Phone className="size-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Video call">
            <Video className="size-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Message">
            <MessageSquare className="size-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default function ContactShowcase() {
  return (
    <div className="space-y-12 p-8">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Contact Card</h1>
        <p className="text-muted-foreground mb-8">
          Card de contato com avatar, status online e botões de ação.
        </p>
      </div>

      {/* Grid View */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-medium">Visualização em Grade</h2>
          <div className="flex gap-2">
            <Badge variant="secondary">851 All Contacts</Badge>
            <Badge variant="outline">62 Pending Invitation</Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <ContactCard
            name="Abdul Kean"
            company="Highspeed Inc."
            initials="AK"
            isOnline
          />
          <ContactCard
            name="Angela Moss"
            company="Highspeed Inc."
            initials="AM"
            isOnline
            isSelected
          />
          <ContactCard
            name="Afiff Skunder"
            company="Highspeed Inc."
            initials="AS"
            isOnline
          />
          <ContactCard
            name="Abigail Smurt"
            company="Highspeed Inc."
            initials="AS"
            isOnline
          />
          <ContactCard
            name="Bella Syuqr"
            company="Highspeed Inc."
            initials="BS"
            isOnline
          />
          <ContactCard
            name="Benny Gacu"
            company="Highspeed Inc."
            initials="BG"
            isOnline
          />
        </div>
      </section>

      {/* With Detail Panel */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Painel de Detalhes</h2>

        <div className="grid lg:grid-cols-[1fr,320px] gap-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <ContactCard
                key={i}
                name="Contact Name"
                company="Highspeed Inc."
                initials="CN"
                isOnline={i % 2 === 0}
              />
            ))}
          </div>

          <Card>
            <CardContent className="p-6 space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex flex-col items-center gap-3 flex-1">
                  <div className="relative">
                    <Avatar className="size-24">
                      <AvatarFallback className="text-xl">AM</AvatarFallback>
                    </Avatar>
                    <span className="absolute bottom-0 right-0 size-5 rounded-full bg-green-500 border-2 border-white" />
                  </div>
                  <div className="text-center">
                    <h3 className="font-semibold text-lg">Angela Moss</h3>
                    <p className="text-sm text-muted-foreground">Super Admin</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon-sm">
                  <X className="size-4" />
                </Button>
              </div>

              <div className="flex items-center justify-center gap-2">
                <Button variant="ghost" size="icon">
                  <Phone className="size-5" />
                </Button>
                <Button variant="ghost" size="icon">
                  <MessageSquare className="size-5" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Video className="size-5" />
                </Button>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">Edit</Button>
                <Button variant="outline" className="flex-1">Remove</Button>
              </div>

              <div className="space-y-2">
                <h4 className="font-semibold">About</h4>
                <p className="text-sm text-muted-foreground">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">Online</p>
            <ContactCard
              name="Peter Parker"
              company="Highspeed Inc."
              initials="PP"
              isOnline
            />
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium">Offline</p>
            <ContactCard
              name="John Doe"
              company="Highspeed Inc."
              initials="JD"
              isOnline={false}
            />
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium">Selected</p>
            <ContactCard
              name="Jane Smith"
              company="Highspeed Inc."
              initials="JS"
              isOnline
              isSelected
            />
          </div>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Composição</h3>
          <p className="text-sm text-muted-foreground">
            Contact Card é composto por: Card + Avatar + Badge (status online) + Button (action buttons)
          </p>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<Card>
  <CardContent className="p-6 space-y-4">
    {/* Avatar com status online */}
    <div className="relative">
      <Avatar className="size-20">
        <AvatarFallback>PP</AvatarFallback>
      </Avatar>
      <span className="absolute bottom-0 right-0 size-4 rounded-full bg-green-500 border-2 border-white" />
    </div>
    
    {/* Nome e empresa */}
    <div className="text-center">
      <h3 className="font-semibold">Peter Parker</h3>
      <p className="text-sm text-muted-foreground">Highspeed Inc.</p>
    </div>

    {/* Action buttons */}
    <div className="flex gap-2">
      <Button variant="ghost" size="icon-sm">
        <Phone className="size-4" />
      </Button>
      <Button variant="ghost" size="icon-sm">
        <Video className="size-4" />
      </Button>
      <Button variant="ghost" size="icon-sm">
        <MessageSquare className="size-4" />
      </Button>
    </div>
  </CardContent>
</Card>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Grid Layout</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {contacts.map(contact => (
    <ContactCard key={contact.id} {...contact} />
  ))}
</div>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Componentes Utilizados</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><code>Card</code> - Container principal</li>
            <li><code>Avatar</code> - Foto/iniciais do contato</li>
            <li><code>Button</code> com variant="ghost" e size="icon-sm" - Botões de ação</li>
            <li><code>Badge</code> - Contadores nas tabs</li>
            <li>Status indicator - Bolinha verde (elemento span)</li>
          </ul>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Botões com aria-label descritivos</li>
            <li>Indicador visual claro de estado online/offline</li>
            <li>Card focável e clicável</li>
            <li>Contraste adequado entre texto e fundo</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
