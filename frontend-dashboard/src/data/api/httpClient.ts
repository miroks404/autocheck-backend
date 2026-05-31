import { API_BASE_URL } from "../../core/config"
import { mapApiErrorMessage } from "../../shared/apiErrors"

export class ApiError extends Error {
  status: number
  details: unknown

  constructor(message: string, status: number, details: unknown = null) {
    super(message)
    this.status = status
    this.details = details
  }
}

function toApiError(payload: Record<string, unknown>, status: number): ApiError {
  const errorObj = payload?.error as { message?: string; details?: unknown } | undefined
  const rawMessage =
    errorObj?.message ||
    (typeof payload?.detail === "string" ? payload.detail : null) ||
    `HTTP ${status}`
  const details = errorObj?.details ?? payload?.detail
  const message = mapApiErrorMessage(rawMessage, details)
  return new ApiError(message, status, details)
}

export async function httpRequestText(method: string, path: string, token?: string | null): Promise<string> {
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(`${API_BASE_URL}${path}`, { method, headers })
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw toApiError(payload as Record<string, unknown>, response.status)
  }
  return response.text()
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
    throw toApiError(payload as Record<string, unknown>, response.status)
  }

  return payload as T
}
