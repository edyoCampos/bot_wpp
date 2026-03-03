"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function AvatarShowcase() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Avatar</h1>
        <p className="text-muted-foreground mb-8">
          Componente de avatar único com tamanhos padronizados e fallback.
        </p>
      </div>

      {/* Sizes */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Tamanhos</h2>
        <div className="flex flex-wrap items-end gap-6">
          <div className="flex flex-col items-center gap-2">
            <Avatar className="size-8">
              <AvatarImage src="https://github.com/shadcn.png" alt="User" />
              <AvatarFallback>CN</AvatarFallback>
            </Avatar>
            <span className="text-xs text-muted-foreground">32px</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Avatar className="size-12">
              <AvatarImage src="https://github.com/shadcn.png" alt="User" />
              <AvatarFallback>CN</AvatarFallback>
            </Avatar>
            <span className="text-xs text-muted-foreground">48px</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Avatar className="size-[59px]">
              <AvatarImage src="https://github.com/shadcn.png" alt="User" />
              <AvatarFallback>CN</AvatarFallback>
            </Avatar>
            <span className="text-xs text-muted-foreground">59px</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Avatar className="size-16">
              <AvatarImage src="https://github.com/shadcn.png" alt="User" />
              <AvatarFallback>CN</AvatarFallback>
            </Avatar>
            <span className="text-xs text-muted-foreground">64px</span>
          </div>
        </div>
      </section>

      {/* With Images */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Com Imagem</h2>
        <div className="flex flex-wrap gap-4">
          <Avatar>
            <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarImage src="https://github.com/vercel.png" alt="@vercel" />
            <AvatarFallback>VC</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarImage src="https://github.com/nextjs.png" alt="@nextjs" />
            <AvatarFallback>NX</AvatarFallback>
          </Avatar>
        </div>
      </section>

      {/* Fallback */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Fallback (Placeholder)</h2>
        <div className="flex flex-wrap gap-4">
          <Avatar>
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback>AB</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback>XY</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback className="bg-primary text-primary-foreground">
              PL
            </AvatarFallback>
          </Avatar>
        </div>
      </section>

      {/* Avatar Group */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Grupo de Avatares</h2>
        <div className="flex -space-x-4">
          <Avatar className="border-2 border-background">
            <AvatarImage src="https://github.com/shadcn.png" alt="User 1" />
            <AvatarFallback>U1</AvatarFallback>
          </Avatar>
          <Avatar className="border-2 border-background">
            <AvatarImage src="https://github.com/vercel.png" alt="User 2" />
            <AvatarFallback>U2</AvatarFallback>
          </Avatar>
          <Avatar className="border-2 border-background">
            <AvatarImage src="https://github.com/nextjs.png" alt="User 3" />
            <AvatarFallback>U3</AvatarFallback>
          </Avatar>
          <Avatar className="border-2 border-background">
            <AvatarFallback>+5</AvatarFallback>
          </Avatar>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Importação</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"`}</code>
          </pre>

          <h3 className="font-medium mt-6">Exemplo Básico</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto">
            <code>{`{/* Com imagem */}
<Avatar>
  <AvatarImage src="/avatars/user.jpg" alt="@username" />
  <AvatarFallback>UN</AvatarFallback>
</Avatar>

{/* Apenas fallback */}
<Avatar>
  <AvatarFallback>JD</AvatarFallback>
</Avatar>

{/* Tamanhos customizados */}
<Avatar className="size-8">
  <AvatarImage src="/avatar.jpg" />
  <AvatarFallback>SM</AvatarFallback>
</Avatar>

<Avatar className="size-16">
  <AvatarImage src="/avatar.jpg" />
  <AvatarFallback>LG</AvatarFallback>
</Avatar>

{/* Grupo com overlap */}
<div className="flex -space-x-4">
  <Avatar className="border-2 border-background">
    <AvatarImage src="/user1.jpg" />
    <AvatarFallback>U1</AvatarFallback>
  </Avatar>
  <Avatar className="border-2 border-background">
    <AvatarImage src="/user2.jpg" />
    <AvatarFallback>U2</AvatarFallback>
  </Avatar>
</div>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Componentes</h3>
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
                  <td className="p-2 font-mono text-sm">Avatar</td>
                  <td className="p-2 text-sm">className</td>
                  <td className="p-2 text-sm">Container principal (size via className)</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">AvatarImage</td>
                  <td className="p-2 text-sm">src, alt</td>
                  <td className="p-2 text-sm">Imagem do avatar</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-mono text-sm">AvatarFallback</td>
                  <td className="p-2 text-sm">children, className</td>
                  <td className="p-2 text-sm">Fallback quando imagem falha/carrega</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3 className="font-medium mt-6">Tamanhos Padrão</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li><code className="bg-muted px-1">size-8</code> → 32px (small)</li>
            <li><code className="bg-muted px-1">size-12</code> → 48px (default)</li>
            <li><code className="bg-muted px-1">size-[59px]</code> → 59px (medium-large)</li>
            <li><code className="bg-muted px-1">size-16</code> → 64px (large)</li>
          </ul>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Sempre forneça <code className="bg-muted px-1">alt</code> descritivo em AvatarImage</li>
            <li>Fallback é automaticamente exibido se a imagem falhar</li>
            <li>Para grupos, considere aria-label no container descrevendo o grupo</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
