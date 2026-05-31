import { useMemo } from "react"
import type { ReportStats, Submission } from "../domain/models"
import { formatUtcToMsk } from "../shared/date"

type Props = {
  stats: ReportStats | null
  submissions: Submission[]
}

export function StatsScreen({ stats, submissions }: Props) {
  const chartPoints = useMemo(() => {
    const today = new Date()
    const days = Array.from({ length: 30 }, (_, index) => {
      const date = new Date(today)
      date.setDate(today.getDate() - (29 - index))
      const key = date.toISOString().slice(0, 10)
      return { key, count: 0 }
    })

    submissions.forEach((submission) => {
      if (!submission.createdAt) return
      const key = submission.createdAt.slice(0, 10)
      const target = days.find((day) => day.key === key)
      if (target) target.count += 1
    })
    return days
  }, [submissions])

  const maxCount = Math.max(1, ...chartPoints.map((p) => p.count))

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>Статистика</h2>
        <p>Метрики за 30 дней, динамика и топ кандидатов</p>
      </header>

      <div className="stats-cards">
        <article className="card">
          <h3>Всего проверок</h3>
          <p className="metric">{stats?.checksLast30Days ?? 0}</p>
        </article>
        <article className="card">
          <h3>Средний балл</h3>
          <p className="metric">{stats?.avgScore ?? 0}</p>
        </article>
        <article className="card">
          <h3>Процент прохождения</h3>
          <p className="metric">{stats?.passRatePct ?? 0}%</p>
        </article>
      </div>

      <article className="card">
        <h3>Динамика проверок (30 дней)</h3>
        <svg className="line-chart" viewBox="0 0 600 220" preserveAspectRatio="none">
          {chartPoints.map((point, index) => {
            if (index === 0) return null
            const prev = chartPoints[index - 1]
            const x1 = ((index - 1) / (chartPoints.length - 1)) * 580 + 10
            const y1 = 200 - (prev.count / maxCount) * 180 + 10
            const x2 = (index / (chartPoints.length - 1)) * 580 + 10
            const y2 = 200 - (point.count / maxCount) * 180 + 10
            return <line key={point.key} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#4c7fff" strokeWidth="2" />
          })}
          {chartPoints.map((point, index) => {
            const cx = (index / (chartPoints.length - 1)) * 580 + 10
            const cy = 200 - (point.count / maxCount) * 180 + 10
            return <circle key={point.key} cx={cx} cy={cy} r="2.5" fill="#00e5a0" />
          })}
        </svg>
      </article>

      <article className="card">
        <h3>Топ кандидатов</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>ФИО</th>
              <th>Лучший балл</th>
              <th>Попыток</th>
            </tr>
          </thead>
          <tbody>
            {(stats?.topCandidates ?? []).map((item) => (
              <tr key={item.candidateId}>
                <td>{item.fullName}</td>
                <td>{item.bestScore}</td>
                <td>{item.attempts}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>

      <article className="card">
        <h3>Последние обновления</h3>
        <ul className="timeline">
          {submissions.slice(0, 6).map((submission) => (
            <li key={submission.id}>
              <span>Проверка #{submission.id}</span>
              <span>{formatUtcToMsk(submission.updatedAt ?? submission.createdAt)}</span>
            </li>
          ))}
        </ul>
      </article>
    </section>
  )
}
