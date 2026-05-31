type Props = { value: number }

export function ProgressBar({ value }: Props) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)))
  const levelClass = clamped > 80 ? "progress-good" : clamped >= 50 ? "progress-mid" : "progress-low"
  return (
    <div className="progress-root" aria-label="progress">
      <div className={`progress-bar ${levelClass}`} style={{ width: `${clamped}%` }} />
      <span className="progress-text">{clamped}%</span>
    </div>
  )
}
