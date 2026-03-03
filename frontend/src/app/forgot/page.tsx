"use client"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { requestPasswordRecovery, normalizeApiError } from "@/services/passwordService"
import { useFormFeedback } from "@/hooks/useFormFeedback"

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useFormFeedback(error, success)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setLoading(true)
    try {
      await requestPasswordRecovery(email)
      setSuccess("Se o email existir, um link de recuperação foi enviado.")
    } catch (err: any) {
      setError(normalizeApiError(err.message || err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-md shadow-lg border rounded-2xl bg-card">
        <CardHeader>
          <h1 className="text-center text-2xl font-bold font-serif mb-2" data-testid="forgot-title">Recuperar senha</h1>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && <div className="text-destructive text-sm" role="alert" aria-live="assertive" data-testid="forgot-error">{error}</div>}
          {success && <div className="text-success text-sm" role="status" aria-live="polite" data-testid="forgot-success">{success}</div>}
          <form className="space-y-4" onSubmit={handleSubmit} aria-label="formulário de recuperação de senha" data-testid="forgot-form">
            <div>
              <Label htmlFor="email" className="font-medium">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoComplete="email"
                aria-label="Email"
                aria-describedby={error ? "forgot-error" : undefined}
                aria-invalid={!!error}
                data-testid="forgot-email"
              />
            </div>
            <Button className="w-full mt-2" type="submit" disabled={loading || !email} aria-label="Enviar recuperação" data-testid="forgot-submit">
              {loading ? "Enviando..." : "Enviar link de recuperação"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
