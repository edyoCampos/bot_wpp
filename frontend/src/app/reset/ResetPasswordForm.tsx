"use client"

import { useState, useRef } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { resetPassword, normalizeApiError } from "@/services/passwordService"
import { useFormFeedback } from "@/hooks/useFormFeedback"
import { useSearchParams } from "next/navigation"

export function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const newPasswordRef = useRef<HTMLInputElement>(null);
  const confirmPasswordRef = useRef<HTMLInputElement>(null);

  useFormFeedback(error, success);

  function focusFirstError() {
    if (!newPassword) {
      newPasswordRef.current?.focus();
      return;
    }
    if (!confirmPassword) {
      confirmPasswordRef.current?.focus();
      return;
    }
    if (newPassword !== confirmPassword) {
      confirmPasswordRef.current?.focus();
      return;
    }
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!token) {
      setError("Link inválido ou expirado. Solicite um novo email de recuperação.");
      return;
    }
    if (!newPassword || !confirmPassword) {
      setError("Preencha todos os campos obrigatórios.");
      focusFirstError();
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("As senhas não coincidem.");
      focusFirstError();
      return;
    }
    setLoading(true);
    try {
      await resetPassword(token, newPassword);
      setSuccess("Senha redefinida com sucesso! Você já pode fazer login.");
    } catch (err: any) {
      setError(normalizeApiError(err.message || err));
      focusFirstError();
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit} aria-label="formulário de redefinição de senha" noValidate data-testid="reset-form">
      <div>
        <Label htmlFor="new-password" className="font-medium">Nova senha</Label>
        <Input
          id="new-password"
          type="password"
          placeholder="Digite a nova senha"
          value={newPassword}
          onChange={e => setNewPassword(e.target.value)}
          required
          minLength={8}
          autoComplete="new-password"
          aria-label="Nova senha"
          aria-invalid={!!error && !newPassword}
          aria-describedby={!!error && !newPassword ? "reset-error" : undefined}
          ref={newPasswordRef}
          data-testid="reset-new-password"
        />
      </div>
      <div>
        <Label htmlFor="confirm-password" className="font-medium">Confirmar nova senha</Label>
        <Input
          id="confirm-password"
          type="password"
          placeholder="Confirme a nova senha"
          value={confirmPassword}
          onChange={e => setConfirmPassword(e.target.value)}
          required
          minLength={8}
          autoComplete="new-password"
          aria-label="Confirmar nova senha"
          aria-invalid={!!error && (!confirmPassword || newPassword !== confirmPassword)}
          aria-describedby={!!error && (!confirmPassword || newPassword !== confirmPassword) ? "reset-error" : undefined}
          ref={confirmPasswordRef}
          data-testid="reset-confirm-password"
        />
      </div>
      <Button className="w-full mt-2" type="submit" disabled={loading || !newPassword || !confirmPassword} aria-label="Redefinir senha" data-testid="reset-submit">
        {loading ? <span className="inline-flex items-center"><span className="loader mr-2" aria-hidden="true"></span>Enviando...</span> : "Redefinir senha"}
      </Button>
      {error && <div id="reset-error" className="text-destructive text-sm" role="alert" aria-live="assertive" data-testid="reset-error">{error}</div>}
      {success && <div className="text-success text-sm" role="status" aria-live="polite" data-testid="reset-success">{success}</div>}
      <span className="sr-only" aria-live="polite">{error ? `Erro: ${error}` : success ? `Sucesso: ${success}` : null}</span>
    </form>
  );
}
