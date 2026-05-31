type InputProps = {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
  disabled?: boolean
  error?: string | null
}

export function Input({ label, value, onChange, placeholder, type = "text", disabled, error }: InputProps) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input
        className={`field-input ${error ? "field-error" : ""}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        type={type}
        disabled={disabled}
      />
      {error ? <span className="field-error-text">{error}</span> : null}
    </label>
  )
}
