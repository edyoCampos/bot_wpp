import { fetchApi, normalizeApiError } from "@/lib/api"

export async function loginApi(email: string, password: string, rememberMe: boolean) {
  const formData = new URLSearchParams()
  formData.append("username", email)
  formData.append("password", password)
  formData.append("rememberMe", rememberMe ? "true" : "false")
  return fetchApi("/api/v1/auth/token", {
    method: "POST",
    body: formData.toString(),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export async function signupApi(email: string, password: string, full_name?: string) {
  return fetchApi("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name }),
  })
}

export { normalizeApiError }
