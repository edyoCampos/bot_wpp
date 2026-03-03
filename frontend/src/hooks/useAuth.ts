import { useState } from "react"
import { loginApi, signupApi, normalizeApiError } from "@/services/authService"

export function useAuth() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)


  async function login(email: string, password: string, rememberMe: boolean) {
    setError(null)
    setLoading(true)
    try {
      await loginApi(email, password, rememberMe)
      setSuccess("Login realizado com sucesso!")
      return true
    } catch (err: any) {
      setError(normalizeApiError(err.message || err))
      return false
    } finally {
      setLoading(false)
    }
  }


  async function signup(email: string, password: string, full_name?: string) {
    setError(null)
    setSuccess(null)
    setLoading(true)
    try {
      await signupApi(email, password, full_name)
      setSuccess("Cadastro realizado com sucesso! Você pode fazer login.")
      return true
    } catch (err: any) {
      setError(normalizeApiError(err.message || err))
      return false
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, success, login, signup, setError, setSuccess }
}
