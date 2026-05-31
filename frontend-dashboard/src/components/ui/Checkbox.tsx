/**
 * Checkbox — базовый элемент формы с состояниями checked/disabled/error.
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
type Props = {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

export function Checkbox({ label, checked, onChange, disabled }: Props) {
  return (
    <label className={`checkbox ${disabled ? "checkbox-disabled" : ""}`}>
      <input type="checkbox" checked={checked} disabled={disabled} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  )
}
