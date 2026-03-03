"use client"

import { MessageInput } from "@/components/ui/message-input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useState } from "react"

export default function MessageInputShowcase() {
  const [messages, setMessages] = useState<string[]>([])

  const handleSend = (message: string) => {
    setMessages([...messages, message])
  }

  return (
    <div className="space-y-12 p-8">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Message Input</h1>
        <p className="text-muted-foreground mb-8">
          Campo de entrada de mensagens com botões de anexo e envio.
        </p>
      </div>

      {/* Basic */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Básico</h2>
        <Card>
          <CardContent className="p-0">
            <MessageInput
              placeholder="Type a message..."
              onSend={handleSend}
            />
          </CardContent>
        </Card>
      </section>

      {/* With All Features */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Todos os Recursos</h2>
        <Card>
          <CardContent className="p-0">
            <MessageInput
              placeholder="Type a message..."
              onSend={handleSend}
              showAttachment
              showImage
              showEmoji
            />
          </CardContent>
        </Card>
      </section>

      {/* Interactive Demo */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Demo Interativo</h2>
        <Card>
          <CardHeader>
            <CardTitle>Enviar Mensagem</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="min-h-[200px] p-4 border rounded-lg space-y-2">
              {messages.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  Digite uma mensagem abaixo...
                </p>
              ) : (
                messages.map((msg, i) => (
                  <div key={i} className="flex gap-2">
                    <div className="px-4 py-2 rounded-2xl bg-primary text-primary-foreground rounded-br-sm max-w-[80%]">
                      <p className="text-sm">{msg}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
          <MessageInput
            placeholder="Type a message..."
            onSend={handleSend}
            showAttachment
            showImage
          />
        </Card>
      </section>

      {/* States */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Estados</h2>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Default</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <MessageInput placeholder="Type a message..." />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Com Anexos</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <MessageInput
                placeholder="Type a message..."
                showAttachment
                showImage
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Disabled</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <MessageInput
                placeholder="You cannot send messages"
                disabled
              />
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
            <code>{`import { MessageInput } from "@/components/ui/message-input"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`const handleSend = (message: string) => {
  console.log('Mensagem enviada:', message)
}

<MessageInput
  placeholder="Type a message..."
  onSend={handleSend}
/>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Com Recursos</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`<MessageInput
  placeholder="Type a message..."
  onSend={handleSend}
  showAttachment
  showImage
  showEmoji
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
                  <td className="p-2 font-mono text-sm">onSend</td>
                  <td className="p-2 text-sm">(message: string) =&gt; void</td>
                  <td className="p-2 text-sm">-</td>
                  <td className="p-2 text-sm">Callback ao enviar</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">placeholder</td>
                  <td className="p-2 text-sm">string</td>
                  <td className="p-2 text-sm">"Type a message..."</td>
                  <td className="p-2 text-sm">Texto placeholder</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">showAttachment</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">true</td>
                  <td className="p-2 text-sm">Botão de anexo</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">showImage</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Botão de imagem</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">showEmoji</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">false</td>
                  <td className="p-2 text-sm">Botão de emoji</td>
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

          <h3 className="font-medium mt-6">Atalhos de Teclado</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><kbd className="px-2 py-1 bg-muted rounded">Enter</kbd> - Envia a mensagem</li>
            <li><kbd className="px-2 py-1 bg-muted rounded">Shift + Enter</kbd> - Nova linha</li>
          </ul>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Botões com aria-label descritivos</li>
            <li>Textarea auto-expandível para mensagens longas</li>
            <li>Botão de envio desabilitado quando vazio</li>
            <li>Navegação via Tab entre controles</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
