"use client"

import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
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
import { signUpSchema, SignUpValues } from "@/lib/validations/auth"

export default function SignupPage() {
  const { loading, error, success, signup, setError, setSuccess } = useAuth()

  // Padroniza feedback visual (toast e mensagem persistente)
  useFormFeedback(error, success)

  const form = useForm<SignUpValues>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
    },
  })

  async function onSubmit(data: SignUpValues) {
    setError(null)
    setSuccess(null)
    const ok = await signup(data.email, data.password, data.full_name)
    if (ok) {
      form.reset()
    }
  }

  return (
    <Card className="w-full max-w-md shadow-lg border rounded-2xl bg-card">
      <CardHeader>
        <h1 className="text-center text-3xl font-bold font-serif mb-2" data-testid="signup-title">
          Criar conta
        </h1>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Feedback visual persistente para acessibilidade */}
        {error && (
          <div className="text-destructive text-sm" role="alert" aria-live="assertive" id="signup-error">
            {error}
          </div>
        )}
        {success && (
          <div className="text-success text-sm" role="status" aria-live="polite" id="signup-success">
            {success}
          </div>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" aria-label="signup form">
            <FormField
              control={form.control}
              name="full_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome completo</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Seu nome (opcional)"
                      type="text"
                      autoComplete="name"
                      data-testid="signup-fullname"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="seu@email.com"
                      type="email"
                      autoComplete="email"
                      data-testid="signup-email"
                      {...field}
                    />
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
                    <Input
                      placeholder="••••••••"
                      type="password"
                      autoComplete="new-password"
                      data-testid="signup-password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button
              className="w-full mt-2"
              type="submit"
              disabled={loading}
              aria-label="Criar conta"
              data-testid="signup-submit"
            >
              {loading ? "Enviando..." : "Criar conta"}
            </Button>
          </form>
        </Form>

        <div className="text-center text-sm mt-4">
          Já tem uma conta?{" "}
          <Link
            href="/signin"
            className="text-primary font-medium hover:underline"
            aria-label="Entrar"
            data-testid="signup-signin"
          >
            Entrar
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
