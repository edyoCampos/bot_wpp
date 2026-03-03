"use client"

import { MessageBubble } from "@/components/ui/message-bubble"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function MessageBubbleShowcase() {
  return (
    <div className="space-y-12 p-8">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Message Bubble</h1>
        <p className="text-muted-foreground mb-8">
          Bolhas de mensagem para threads de chat e conversas.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <MessageBubble
              sender="other"
              senderName="Peter Parker"
              senderInitials="PP"
              message="Olá! Como você está?"
              timestamp="10:30"
            />
            <MessageBubble
              sender="user"
              message="Estou bem, obrigado! E você?"
              timestamp="10:32"
            />
          </CardContent>
        </Card>
      </section>

      {/* Thread Example */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Thread de Conversa</h2>
        <Card>
          <CardHeader>
            <CardTitle>Conversa com Roberto Chávez</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <MessageBubble
              sender="other"
              senderName="Roberto Chávez"
              senderInitials="RC"
              message="We're all taking things straight forward as our designers said that it will make our product stand out from our current competitor."
              timestamp="09:56 Am"
            />
            <MessageBubble
              sender="user"
              message="Add the RSVP and invitations page as well. We'll discuss the information architecture before that."
              timestamp="09:58 Am"
            />
            <MessageBubble
              sender="other"
              senderName="Roberto Chávez"
              senderInitials="RC"
              message="No, I think we should change the layer and add another layer for the design to work out right. Tell me what you think of the design and if there's any change we could change so the output will be much better."
              timestamp="09:59 Am"
            />
            <MessageBubble
              sender="user"
              message="Hmm yeah, we could try that option too. Did we have any progress with the design that John sent?"
              timestamp="10:02 Am"
            />
            <MessageBubble
              sender="other"
              senderName="Roberto Chávez"
              senderInitials="RC"
              message="Lorem ipsum dolor sit amet, consectetur adipiscing elit et ultricesq."
              timestamp="10:12 Am"
              unread
            />
          </CardContent>
        </Card>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Mensagem do outro usuário</p>
              <MessageBubble
                sender="other"
                senderName="Karmo Tjass"
                senderInitials="KT"
                message="Lorem ipsum dolor sit amet, consectet adipiscing elit et ultricesq voluptat elit et ultricesq."
                timestamp="11:23 Am"
              />
            </div>
            <div>
              <p className="text-sm font-medium mb-2">Mensagem do usuário</p>
              <MessageBubble
                sender="user"
                message="Tell me what you think of the design and if there's any thing that we should change for the output."
                timestamp="11:25 Am"
              />
            </div>
            <div>
              <p className="text-sm font-medium mb-2">Não lida (com destaque)</p>
              <MessageBubble
                sender="other"
                senderName="Karmo Tjass"
                senderInitials="KT"
                message="New message just arrived!"
                timestamp="11:30 Am"
                unread
              />
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
            <code>{`import { MessageBubble } from "@/components/ui/message-bubble"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Mensagem de outro usuário */}
<MessageBubble
  sender="other"
  senderName="Peter Parker"
  senderInitials="PP"
  message="Hello!"
  timestamp="10:30"
/>

{/* Mensagem do usuário atual */}
<MessageBubble
  sender="user"
  message="Hi there!"
  timestamp="10:32"
/>`}</code>
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
                  <td className="p-2 font-mono text-sm">sender</td>
                  <td className="p-2 text-sm">"user" | "other"</td>
                  <td className="p-2 text-sm">"other"</td>
                  <td className="p-2 text-sm">Define alinhamento e cor</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">message</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">-</td>
                  <td className="p-2 text-sm">Texto da mensagem</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">timestamp</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">-</td>
                  <td className="p-2 text-sm">Horário da mensagem</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">senderName</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">-</td>
                  <td className="p-2 text-sm">Nome do remetente</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">senderInitials</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">"JD"</td>
                  <td className="p-2 text-sm">Iniciais para avatar</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">unread</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Destaque de não lida</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Use role="log" no container da thread para atualizações automáticas</li>
            <li>Timestamps ajudam usuários com leitores de tela</li>
            <li>Contraste adequado entre texto e fundo</li>
            <li>Indicador visual claro de mensagens não lidas</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
