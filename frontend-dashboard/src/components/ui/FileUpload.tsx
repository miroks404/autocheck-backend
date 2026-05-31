import { useState } from "react"

type Props = {
  file: File | null
  onFileChange: (file: File | null) => void
  error?: string | null
}

const MAX_SIZE = 50 * 1024 * 1024

function validateZip(file: File): string | null {
  if (!file.name.toLowerCase().endsWith(".zip")) return "Допустим только .zip"
  if (file.size > MAX_SIZE) return "Размер файла не должен превышать 50 МБ"
  return null
}

export function FileUpload({ file, onFileChange, error }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)

  const applyFile = (next: File | null) => {
    if (!next) {
      onFileChange(null)
      setLocalError(null)
      return
    }
    const validationError = validateZip(next)
    setLocalError(validationError)
    onFileChange(validationError ? null : next)
  }

  const displayError = error ?? localError

  return (
    <div
      className={`upload-box ${dragOver ? "upload-dragover" : ""} ${displayError ? "upload-error" : ""}`}
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragOver(false)
        applyFile(e.dataTransfer.files?.[0] ?? null)
      }}
    >
      <label className="upload-label">
        <input
          type="file"
          accept=".zip"
          onChange={(e) => applyFile(e.target.files?.[0] ?? null)}
          className="upload-input"
        />
        <span>{file ? `Файл: ${file.name}` : "Перетащите ZIP или выберите файл"}</span>
      </label>
      <small>Допустим только .zip до 50 МБ</small>
      {displayError ? <p className="field-error-text">{displayError}</p> : null}
    </div>
  )
}
