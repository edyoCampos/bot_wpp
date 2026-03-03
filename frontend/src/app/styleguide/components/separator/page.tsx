"use client"

import { Separator } from "@/components/ui/separator"

export default function SeparatorShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Separator (Divider)</h1>
        <p className="text-muted-foreground mb-8">
          Linha separadora horizontal ou vertical para organização visual.
        </p>
      </div>

      {/* Horizontal */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Horizontal</h2>
        <div className="space-y-6">
          <div>
            <p className="mb-4">Separador padrão</p>
            <Separator />
          </div>
          <div>
            <p className="mb-4">Separador com opacidade reduzida (subtle)</p>
            <Separator className="opacity-50" />
          </div>
          <div>
            <p className="mb-4">Separador mais forte (strong)</p>
            <Separator className="bg-border h-[2px]" />
          </div>
        </div>
      </section>

      {/* Vertical */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Vertical</h2>
        <div className="flex items-center gap-4 h-12">
          <span>Item 1</span>
          <Separator orientation="vertical" />
          <span>Item 2</span>
          <Separator orientation="vertical" />
          <span>Item 3</span>
          <Separator orientation="vertical" className="opacity-50" />
          <span>Item 4</span>
        </div>
      </section>

      {/* In Context */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Em Contexto</h2>
        <div className="max-w-md space-y-1 rounded-lg border p-6">
          <div className="space-y-1">
            <h3 className="text-lg font-semibold">Configurações</h3>
            <p className="text-sm text-muted-foreground">
              Gerencie suas preferências de conta
            </p>
          </div>
          <Separator className="my-4" />
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium">Perfil</h4>
              <p className="text-sm text-muted-foreground">
                Atualize suas informações pessoais
              </p>
            </div>
            <Separator />
            <div>
              <h4 className="text-sm font-medium">Notificações</h4>
              <p className="text-sm text-muted-foreground">
                Configure como você recebe alertas
              </p>
            </div>
            <Separator />
            <div>
              <h4 className="text-sm font-medium">Privacidade</h4>
              <p className="text-sm text-muted-foreground">
                Controle quem pode ver suas informações
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Separator } from "@/components/ui/separator"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Horizontal (padrão) */}
<Separator />

{/* Vertical */}
<Separator orientation="vertical" />

{/* Com intensidade customizada */}
<Separator className="opacity-50" />
<Separator className="bg-border h-[2px]" />

{/* Em contexto */}
<div>
  <h3>Título</h3>
  <Separator className="my-4" />
  <p>Conteúdo abaixo do separador</p>
</div>`}</code>
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
                  <td className="p-2 font-mono text-sm">orientation</td>
                  <td className="p-2 text-sm">"horizontal" | "vertical"</td>
                  <td className="p-2 text-sm">"horizontal"</td>
                  <td className="p-2 text-sm">Direção do separador</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">decorative</td>
                  <td className="p-2 text-sm">boolean</td>
                  <td className="p-2 text-sm">true</td>
                  <td className="p-2 text-sm">Se é apenas visual (não semântico)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Variantes de Tom</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Subtle (sutil) */}
<Separator className="opacity-50" />

{/* Strong (forte) */}
<Separator className="bg-border h-[2px]" />`}</code>
          </pre>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Por padrão é decorativo (role="none")</li>
            <li>Para separação semântica, defina decorative=false (role="separator")</li>
            <li>Orientação vertical requer altura explícita do container</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
