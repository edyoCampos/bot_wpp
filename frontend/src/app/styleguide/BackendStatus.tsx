import { fetchApi } from '@/lib/api'
import { useEffect, useState } from 'react'

export default function BackendStatus() {
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchApi<{ status: string }>('/health')
      .then((data) => setStatus(data.status))
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <div className="text-red-500">Erro: {error}</div>
  if (!status) return <div>Carregando status do backend...</div>
  return <div className="text-green-600">Backend: {status}</div>
}
