import { useMemo, useState } from "react"
import type { AiReview, Assignment, CheckResult, Submission, Verdict } from "../domain/models"
import { ScoreCard } from "../components/ui/ScoreCard"
import { Button } from "../components/ui/Button"
import { StatusBadge } from "../components/ui/StatusBadge"
import { formatUtcToMsk } from "../shared/date"

type Props = {
  submission: Submission | null
  assignment: Assignment | null
  results: CheckResult[]
  aiReview: AiReview | null
  onLoadAiReview: () => Promise<void>
  onDownloadReport: () => Promise<void>
  onSetVerdict: (verdict: Verdict) => Promise<void>
  canSetVerdict: boolean
}

export function SubmissionDetailsScreen({
  submission,
  assignment,
  results,
  aiReview,
  onLoadAiReview,
  onDownloadReport,
  onSetVerdict,
  canSetVerdict,
}: Props) {
  const [expandedChecker, setExpandedChecker] = useState<string | null>(null)

  const timeline = useMemo(() => {
    if (!submission) return []
    return [
      { label: "Загрузка", value: formatUtcToMsk(submission.createdAt) },
      { label: "Запуск проверок", value: formatUtcToMsk(submission.updatedAt) },
      { label: "Текущий статус", value: submission.status },
      { label: "Вердикт", value: submission.verdict },
    ]
  }, [submission])

  if (!submission) {
    return (
      <section className="panel">
        <header className="panel-header">
          <h2>Карточка проверки</h2>
          <p>Выберите строку в таблице дашборда</p>
        </header>
      </section>
    )
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>Карточка проверки #{submission.id}</h2>
        <p>Детализация чекеров, AI-анализ, вердикт и хронология</p>
      </header>

      <ScoreCard
        title={assignment?.title ?? `Assignment #${submission.assignmentId}`}
        candidate={`Candidate #${submission.candidateId}`}
        score={submission.finalScore}
        status={submission.status}
      />

      <div className="details-grid">
        <article className="card">
          <h3>Детализация проверок</h3>
          {results.map((result) => (
            <div key={result.checker} className="result-row">
              <button className="result-summary" onClick={() => setExpandedChecker(expandedChecker === result.checker ? null : result.checker)}>
                <span>{result.checker}</span>
                <StatusBadge status={result.status} />
                <strong>{result.score}</strong>
              </button>
              {expandedChecker === result.checker ? (
                <pre className="result-details">{JSON.stringify(result.details ?? result.message, null, 2)}</pre>
              ) : null}
            </div>
          ))}
        </article>

        <article className="card">
          <h3>AI-анализ</h3>
          {aiReview ? (
            aiReview.available ? (
              <div className="ai-review">
                <p>{aiReview.summary}</p>
                <h4>Сильные стороны</h4>
                <ul>
                  {aiReview.strengths.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                <h4>Улучшения</h4>
                <ul>
                  {aiReview.improvements.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="ai-unavailable">AI-анализ недоступен</p>
            )
          ) : (
            <Button variant="secondary" onClick={onLoadAiReview}>
              Загрузить AI-анализ
            </Button>
          )}
          <div className="button-row">
            <Button variant="secondary" onClick={onDownloadReport}>
              Скачать отчёт
            </Button>
            {canSetVerdict ? (
              <>
                <Button onClick={() => onSetVerdict("approved")}>Принять</Button>
                <Button variant="danger" onClick={() => onSetVerdict("rejected")}>
                  Отклонить
                </Button>
              </>
            ) : null}
          </div>
        </article>
      </div>

      <article className="card">
        <h3>Хронология событий</h3>
        <ul className="timeline">
          {timeline.map((item) => (
            <li key={item.label}>
              <span>{item.label}</span>
              <span>{item.value}</span>
            </li>
          ))}
        </ul>
      </article>
    </section>
  )
}
