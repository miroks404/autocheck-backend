const API_ERROR_MESSAGES: Record<string, string> = {
  "Email belongs to a non-candidate user":
    "Этот email уже занят экспертом или администратором. Укажите email кандидата.",
  "Email принадлежит эксперту или администратору, укажите email кандидата":
    "Этот email уже занят экспертом или администратором. Укажите email кандидата.",
  "Either git_url or zip_path must be provided": "Укажите Git URL или загрузите ZIP-файл.",
  "Git URL must start with https://": "Git URL должен начинаться с https://",
  "Only .zip files are allowed": "Допустим только файл .zip",
  "ZIP file exceeds 50MB limit": "Размер ZIP не должен превышать 50 МБ",
  "Validation failed": "Проверьте корректность заполнения полей",
}

type ValidationDetail = {
  loc?: Array<string | number>
  msg?: string
}

export function mapApiErrorMessage(message: string, details?: unknown): string {
  if (API_ERROR_MESSAGES[message]) return API_ERROR_MESSAGES[message]

  if (Array.isArray(details)) {
    const parts = (details as ValidationDetail[])
      .map((item) => {
        const field = item.loc?.filter((part) => part !== "body").join(".") || "поле"
        return `${field}: ${item.msg ?? "ошибка"}`
      })
      .filter(Boolean)
    if (parts.length > 0) return parts.join("; ")
  }

  return message
}
