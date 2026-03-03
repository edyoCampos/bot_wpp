import { fetchApi, normalizeApiError } from "@/lib/api"

export async function requestPasswordRecovery(email: string) {
  const formData = new URLSearchParams()
  formData.append("email", email)
  return fetchApi("/api/v1/auth/password-recovery", {
    method: "POST",
    body: formData.toString(),
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export async function resetPassword(token: string, new_password: string) {
  return fetchApi("/api/v1/auth/password-reset", {
    method: "POST",
    body: JSON.stringify({ token, new_password }),
  })
}

export { normalizeApiError }
