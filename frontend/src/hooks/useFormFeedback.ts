import { useEffect } from "react"
import { toast } from "sonner"

/**
 * Padroniza feedback visual de formulários (erro/sucesso via toast e mensagem persistente).
 * Chame dentro do componente de página.
 * @param error Mensagem de erro (string|null)
 * @param success Mensagem de sucesso (string|null)
 * @param opts Configurações opcionais
 */
export function useFormFeedback(
  error: string | null,
  success: string | null,
  opts?: { toastOnError?: boolean; toastOnSuccess?: boolean }
) {
  useEffect(() => {
    if (error && opts?.toastOnError !== false) {
      toast.error(error)
    }
  }, [error, opts?.toastOnError])

  useEffect(() => {
    if (success && opts?.toastOnSuccess !== false) {
      toast.success(success)
    }
  }, [success, opts?.toastOnSuccess])
}
