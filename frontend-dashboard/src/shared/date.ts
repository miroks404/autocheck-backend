export function formatUtcToMsk(value?: string | null): string {
  if (!value) return "—"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return "—"

  const utcMillis = date.getTime() + date.getTimezoneOffset() * 60_000
  const msk = new Date(utcMillis + 3 * 60 * 60_000)

  const dd = String(msk.getDate()).padStart(2, "0")
  const mm = String(msk.getMonth() + 1).padStart(2, "0")
  const yyyy = msk.getFullYear()
  const hh = String(msk.getHours()).padStart(2, "0")
  const min = String(msk.getMinutes()).padStart(2, "0")
  return `${dd}.${mm}.${yyyy} ${hh}:${min}`
}
