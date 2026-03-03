
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3333';


export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit & { timeout?: number; onError?: (err: Error, endpoint: string) => void }
): Promise<T> {
  let controller: AbortController | undefined;
  let timeoutId: NodeJS.Timeout | undefined;
  let signal = options?.signal;
  if (options?.timeout) {
    controller = new AbortController();
    signal = controller.signal;
    timeoutId = setTimeout(() => controller!.abort(), options.timeout);
  }
  try {
    const headers: Record<string, string> = {};
    if (options?.headers) {
      if (options.headers instanceof Headers) {
        for (const [key, value] of options.headers.entries()) {
          headers[key] = value;
        }
      } else if (Array.isArray(options.headers)) {
        for (const [key, value] of options.headers) {
          headers[key] = value;
        }
      } else {
        Object.assign(headers, options.headers as Record<string, string>);
      }
    }
    if (!headers['Content-Type'] && !headers['content-type']) {
      headers['Content-Type'] = 'application/json';
    }
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      signal,
      headers,
    });
    if (!res.ok) {
      let errorMessage = `API error: ${res.status}`;
      try {
        const data = await res.json();
        errorMessage = normalizeApiError(data, res.status);
      } catch (e) {}
      const error = new Error(errorMessage);
      (error as any).status = res.status;
      if (typeof options?.onError === 'function') {
        options.onError(error, endpoint);
      }
      throw error;
    }
    return res.json();
  } catch (err: any) {
    if (typeof options?.onError === 'function') {
      options.onError(err, endpoint);
    }
    throw err;
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}

export function normalizeApiError(data: any, status?: number): string {
  if (!data) return "Ocorreu um erro inesperado. Tente novamente.";

  // FastAPI: string detail (ex: token inválido)
  if (typeof data.detail === 'string') {
    const detail = data.detail.toLowerCase();
    if (detail.includes('expired')) {
      return "Este link de redefinição expirou.";
    }
    if (detail.includes('already used')) {
      return "Este link de redefinição já foi utilizado.";
    }
    if (detail.includes('invalid signature') || detail.includes('invalid token') || detail.includes('token')) {
      return "O link de redefinição é inválido ou está corrompido.";
    }
    if (detail.includes('not found')) {
      return "Recurso não encontrado.";
    }
    return "Ocorreu um erro ao validar o link. Tente novamente!";
  }

  // FastAPI: validation error array
  if (Array.isArray(data.detail)) {
    const messages = data.detail.map((err: any) => {
      if (err.msg && err.loc) {
        // Campos obrigatórios
        if (err.msg.toLowerCase().includes('field required')) {
          return null; // Não mostrar nomes técnicos
        }
        // Senha muito curta
        if (err.loc.includes('new_password') && err.msg.toLowerCase().includes('shorter than')) {
          return "A senha é muito curta. Use pelo menos 8 caracteres.";
        }
      }
      return null;
    }).filter(Boolean);
    if (messages.length > 0) {
      return messages.join(' ');
    }
    // Se só campos obrigatórios faltando
    if (data.detail.some((err: any) => err.msg && err.msg.toLowerCase().includes('field required'))) {
      return "Preencha todos os campos obrigatórios.";
    }
    return "Ocorreu um erro ao validar os dados. Tente novamente!";
  }

  if (data.message) {
    if (typeof data.message === 'string') {
      const msg = data.message.toLowerCase();
      if (msg.includes('expired')) {
        return "Este link de redefinição expirou. Solicite um novo para redefinir sua senha.";
      }
      if (msg.includes('already used')) {
        return "Este link de redefinição já foi utilizado. Solicite um novo para redefinir sua senha.";
      }
      if (msg.includes('invalid signature') || msg.includes('invalid token') || msg.includes('token')) {
        return "O link de redefinição é inválido ou está corrompido. Solicite um novo para redefinir sua senha.";
      }
      if (msg.includes('not found')) {
        return "Recurso não encontrado.";
      }
      return "Ocorreu um erro ao validar o link. Tente novamente!";
    }
  }

  return "Ocorreu um erro inesperado. Tente novamente.";
}
