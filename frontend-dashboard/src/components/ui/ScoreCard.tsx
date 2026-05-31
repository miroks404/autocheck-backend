import { StatusBadge } from "./StatusBadge"

type Props = {
  title: string
  candidate: string
  score: number | null
  status: "pending" | "running" | "done" | "error" | "passed" | "failed"
}

export function ScoreCard({ title, candidate, score, status }: Props) {
  const scoreClass = score === null ? "" : score >= 80 ? "score-good" : score >= 50 ? "score-mid" : "score-low"
  return (
    <article className="score-card">
      <div className="score-card-header">
        <h3>{title}</h3>
        <StatusBadge status={status} />
      </div>
      <p className="score-card-candidate">{candidate}</p>
      <p className={`score-card-value ${scoreClass}`}>{score === null ? "—" : Math.round(score)}</p>
    </article>
  )
}
