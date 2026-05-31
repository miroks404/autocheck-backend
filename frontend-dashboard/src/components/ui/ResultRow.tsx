/**
 * ResultRow — строка результата чекера с раскрываемыми деталями.
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
import type { CheckResult } from "../../domain/models"
import { checkerLabel } from "../../shared/labels"
import { StatusBadge } from "./StatusBadge"
import { ProgressBar } from "./ProgressBar"

type Props = {
  result: CheckResult
  expanded: boolean
  onToggle: () => void
}

export function ResultRow({ result, expanded, onToggle }: Props) {
  return (
    <div className="result-row">
      <button type="button" className="result-summary" onClick={onToggle} aria-expanded={expanded}>
        <span>{checkerLabel(result.checker)}</span>
        <StatusBadge status={result.status} />
        <ProgressBar value={result.score} />
        <span className="result-chevron">{expanded ? "▲" : "▼"}</span>
      </button>
      {expanded ? (
        <pre className="result-details">{JSON.stringify(result.details ?? result.message, null, 2)}</pre>
      ) : null}
    </div>
  )
}
