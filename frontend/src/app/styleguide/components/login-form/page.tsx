"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Eye, EyeOff, Mail } from "lucide-react"

export default function LoginFormShowcase() {
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  return (
    <div className="space-y-12 p-8">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Login Form</h1>
        <p className="text-muted-foreground mb-8">
          Formulário de login com autenticação tradicional e social.
        </p>
      </div>

      {/* Full Login Form */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Layout Completo</h2>

        <div className="flex justify-center">
          <div className="w-full max-w-4xl space-y-6">
            {/* Logo/Avatar */}
            <div className="flex justify-center">
              <Avatar className="size-16">
                <AvatarFallback className="bg-muted">
                  <span className="text-2xl">V</span>
                </AvatarFallback>
              </Avatar>
            </div>

            {/* Title */}
            <h2 className="text-2xl font-semibold text-center">Log in</h2>

            {/* Form Card */}
            <Card>
              <CardContent className="p-8">
                <div className="grid md:grid-cols-[1fr,auto,1fr] gap-8 items-start">
                  {/* Left Side - Traditional Login */}
                  <div className="space-y-6">
                    <h3 className="font-medium">Log in</h3>

                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="email">Email address</Label>
                        <Input
                          id="email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="your@email.com"
                        />
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="password">Password</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-auto p-0 text-sm"
                            onClick={() => setShowPassword(!showPassword)}
                          >
                            {showPassword ? (
                              <>
                                <EyeOff className="size-3 mr-1" />
                                Hide
                              </>
                            ) : (
                              <>
                                <Eye className="size-3 mr-1" />
                                Show
                              </>
                            )}
                          </Button>
                        </div>
                        <Input
                          id="password"
                          type={showPassword ? "text" : "password"}
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="••••••••"
                        />
                      </div>

                      <Button
                        className="w-full"
                        disabled={!email || !password}
                      >
                        Log in
                      </Button>
                    </div>
                  </div>

                  {/* Divider */}
                  <div className="flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                      <Separator orientation="vertical" className="h-48" />
                      <span className="text-sm text-muted-foreground font-medium">OR</span>
                    </div>
                  </div>

                  {/* Right Side - Social Login */}
                  <div className="space-y-4">
                    <Button
                      variant="outline"
                      className="w-full justify-start gap-3"
                    >
                      <svg className="size-5" viewBox="0 0 24 24">
                        <path
                          fill="currentColor"
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        />
                        <path
                          fill="currentColor"
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        />
                        <path
                          fill="currentColor"
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                        />
                        <path
                          fill="currentColor"
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        />
                      </svg>
                      Continue with Google
                    </Button>

                    <Button
                      variant="outline"
                      className="w-full justify-start gap-3"
                    >
                      <svg className="size-5" fill="#1877F2" viewBox="0 0 24 24">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                      </svg>
                      Continue with Facebook
                    </Button>

                    <Button
                      variant="outline"
                      className="w-full justify-start gap-3"
                    >
                      <Mail className="size-5" />
                      Sign up with email
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Footer Links */}
            <div className="text-center space-y-2">
              <Button variant="link" className="text-sm">
                Can't log in?
              </Button>
              <p className="text-xs text-muted-foreground">
                Secure login with reCAPTCHA subject to Google Terms & Privacy
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Components Breakdown */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Componentes Utilizados</h2>
        <Card>
          <CardContent className="p-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h3 className="font-medium">Estrutura</h3>
                <ul className="text-sm space-y-2">
                  <li>✅ <code>Card</code> - Container do formulário</li>
                  <li>✅ <code>Avatar</code> - Logo/ícone do app</li>
                  <li>✅ <code>Separator</code> - Divisor vertical "OR"</li>
                </ul>
              </div>
              <div className="space-y-3">
                <h3 className="font-medium">Form Elements</h3>
                <ul className="text-sm space-y-2">
                  <li>✅ <code>Input</code> - Email e Password</li>
                  <li>✅ <code>Label</code> - Rótulos dos campos</li>
                  <li>✅ <code>Button</code> - Submit e social auth</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Variations */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Variações</h2>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Simple Login */}
          <Card>
            <CardHeader>
              <h3 className="font-medium">Login Simples</h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email-simple">Email</Label>
                <Input id="email-simple" type="email" placeholder="your@email.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password-simple">Password</Label>
                <Input id="password-simple" type="password" placeholder="••••••••" />
              </div>
              <Button className="w-full">Log in</Button>
              <Button variant="link" className="w-full text-sm">
                Forgot password?
              </Button>
            </CardContent>
          </Card>

          {/* Social Only */}
          <Card>
            <CardHeader>
              <h3 className="font-medium">Somente Social</h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start gap-3">
                <svg className="size-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                </svg>
                Continue with Google
              </Button>
              <Button variant="outline" className="w-full justify-start gap-3">
                <svg className="size-5" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
                Continue with Facebook
              </Button>
              <Separator className="my-4" />
              <Button variant="outline" className="w-full">
                Sign up with email
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-2xl font-medium">Uso</h2>
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h3 className="font-medium">Código de Exemplo</h3>
          <pre className="bg-muted p-4 rounded overflow-x-auto text-xs">
            <code>{`<Card>
  <CardContent className="p-8">
    <div className="space-y-4">
      {/* Email Input */}
      <div className="space-y-2">
        <Label htmlFor="email">Email address</Label>
        <Input id="email" type="email" />
      </div>

      {/* Password with Toggle */}
      <div className="space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="password">Password</Label>
          <Button variant="ghost" size="sm">
            {showPassword ? "Hide" : "Show"}
          </Button>
        </div>
        <Input 
          id="password" 
          type={showPassword ? "text" : "password"} 
        />
      </div>

      {/* Submit Button */}
      <Button className="w-full">Log in</Button>

      {/* Divider */}
      <div className="relative">
        <Separator />
        <span className="absolute inset-0 flex items-center justify-center">
          <span className="bg-background px-2 text-sm text-muted-foreground">
            OR
          </span>
        </span>
      </div>

      {/* Social Buttons */}
      <Button variant="outline" className="w-full">
        <GoogleIcon /> Continue with Google
      </Button>
    </div>
  </CardContent>
</Card>`}</code>
          </pre>

          <h3 className="font-medium mt-6">Best Practices</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Use type="email" para ativar teclado de email no mobile</li>
            <li>Botão de submit desabilitado quando campos estão vazios</li>
            <li>Toggle show/hide password para melhor UX</li>
            <li>Links claros para recuperação de senha</li>
            <li>Ícones reconhecíveis para autenticação social</li>
          </ul>

          <h3 className="font-medium mt-6">Acessibilidade</h3>
          <ul className="list-disc list-inside space-y-2 text-sm">
            <li>Labels associados com inputs via htmlFor/id</li>
            <li>Autocomplete apropriado (email, current-password)</li>
            <li>Mensagens de erro claras e descritivas</li>
            <li>Navegação por Tab em ordem lógica</li>
            <li>Enter submete o formulário</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
