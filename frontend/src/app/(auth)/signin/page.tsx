"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Lock, User } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/hooks/useAuth"
import { useFormFeedback } from "@/hooks/useFormFeedback"
import { signInSchema, SignInValues } from "@/lib/validations/auth"

function SignInForm() {
  const { loading, error, success, login, setError } = useAuth()
  const searchParams = useSearchParams()

  // Padroniza feedback visual (toast e mensagem persistente)
  useFormFeedback(error, success)

  const form = useForm<SignInValues>({
    resolver: zodResolver(signInSchema),
    defaultValues: {
      email: "",
      password: "",
      remember: false,
    },
  })

  async function onSubmit(data: SignInValues) {
    setError(null)
    await login(data.email, data.password, data.remember ?? false)
  }

  return (
    <Card className="w-full max-w-md shadow-lg border rounded-2xl bg-card">
      <CardHeader>
        <h1 className="text-center text-3xl font-bold font-serif mb-2" data-testid="login-title">
          Entrar
        </h1>
        {searchParams.get("verified") === "1" && (
          <div
            className="text-center text-green-600 text-sm bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800"
            role="status"
            aria-live="polite"
          >
            ✅ Email verificado com sucesso! Agora você pode fazer login.
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Feedback visual persistente para acessibilidade */}
        {error && (
          <div className="text-destructive text-sm" role="alert" aria-live="assertive" id="login-error">
            {error}
          </div>
        )}
        {success && (
          <div className="text-success text-sm" role="status" aria-live="polite" id="login-success">
            {success}
          </div>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" aria-label="login form">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        placeholder="seu@email.com"
                        type="email"
                        className="pl-10"
                        autoComplete="email"
                        data-testid="login-username"
                        {...field}
                      />
                      <User className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Senha</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        placeholder="••••••••"
                        type="password"
                        className="pl-10"
                        autoComplete="current-password"
                        data-testid="login-password"
                        {...field}
                      />
                      <Lock className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex items-center justify-between">
              <FormField
                control={form.control}
                name="remember"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-start space-x-2 space-y-0 text-sm">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        data-testid="login-remember"
                        id="remember"
                      />
                    </FormControl>
                    <div className="leading-none">
                      <FormLabel htmlFor="remember" className="text-sm font-normal cursor-pointer">
                        Lembrar de mim
                      </FormLabel>
                    </div>
                  </FormItem>
                )}
              />
              <Link
                href="/forgot"
                className="text-sm text-primary hover:underline"
                aria-label="Esqueceu a senha?"
                data-testid="login-forgot"
              >
                Esqueceu a senha?
              </Link>
            </div>

            <Button
              className="w-full mt-2"
              type="submit"
              aria-label="Entrar"
              data-testid="login-submit"
              disabled={loading}
            >
              {loading ? "Enviando..." : "Entrar"}
            </Button>
          </form>
        </Form>

        <div className="text-center text-sm mt-4">
          Novo por aqui?{" "}
          <Link
            href="/signup"
            className="text-primary font-medium hover:underline"
            aria-label="Criar conta"
            data-testid="login-signup"
          >
            Criar conta
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}

export default function SignInPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center p-8">Loading...</div>}>
      <SignInForm />
    </Suspense>
  )
}
