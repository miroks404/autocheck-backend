/**
 * FilterChip — чип активного фильтра с кнопкой сброса.
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
type Props = {
  label: string
  onRemove: () => void
}

export function FilterChip({ label, onRemove }: Props) {
  return (
    <span className="filter-chip">
      {label}
      <button type="button" aria-label={`Сбросить фильтр ${label}`} onClick={onRemove}>
        ×
      </button>
    </span>
  )
}
