import { API_BASE_URL } from "../../core/config"

export class ApiError extends Error {
  status: number
  details: unknown

  constructor(message: string, status: number, details: unknown = null) {
    super(message)
    this.status = status
    this.details = details
  }
}

export async function httpRequest<T>(
  method: string,
  path: string,
  token?: string | null,
  body?: BodyInit | object,
  asFormData = false,
): Promise<T> {
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  if (body && !asFormData) headers["Content-Type"] = "application/json"

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? (asFormData ? (body as BodyInit) : JSON.stringify(body)) : undefined,
  })
  const payload = await response.json().catch(() => ({}))

  if (!response.ok) {
    const message = payload?.error?.message || payload?.detail || `HTTP ${response.status}`
    throw new ApiError(message, response.status, payload?.error?.details || payload?.detail)
  }

  return payload as T
}
