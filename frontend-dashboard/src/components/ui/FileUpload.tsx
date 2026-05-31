type Props = {
  file: File | null
  onFileChange: (file: File | null) => void
  error?: string | null
}

export function FileUpload({ file, onFileChange, error }: Props) {
  return (
    <div className={`upload-box ${error ? "upload-error" : ""}`}>
      <label className="upload-label">
        <input
          type="file"
          accept=".zip"
          onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
          className="upload-input"
        />
        <span>{file ? `Файл: ${file.name}` : "Перетащите ZIP или выберите файл"}</span>
      </label>
      <small>Допустим только .zip до 50 МБ</small>
      {error ? <p className="field-error-text">{error}</p> : null}
    </div>
  )
}
