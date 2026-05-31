/**
 * SubmissionDetailsScreen — карточка проверки с чекерами, AI-анализом, вердиктом и хронологией.
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
import { useState } from "react"
import type { AiReview, Assignment, CheckResult, Submission, TimelineEvent, Verdict } from "../domain/models"
import { ScoreCard } from "../components/ui/ScoreCard"
import { Button } from "../components/ui/Button"
import { ResultRow } from "../components/ui/ResultRow"
import { ProgressBar } from "../components/ui/ProgressBar"
import { formatUtcToMsk } from "../shared/date"
import { VERDICT_LABELS } from "../shared/labels"

type Props = {
  submission: Submission | null
  assignment: Assignment | null
  results: CheckResult[]
  timeline: TimelineEvent[]
  aiReview: AiReview | null
  onLoadAiReview: () => Promise<void>
  onDownloadReport: () => Promise<void>
  onSetVerdict: (verdict: Verdict, comment: string) => Promise<void>
  canSetVerdict: boolean
}

export function SubmissionDetailsScreen({
  submission,
  assignment,
  results,
  timeline,
  aiReview,
  onLoadAiReview,
  onDownloadReport,
  onSetVerdict,
  canSetVerdict,
}: Props) {
  const [expandedChecker, setExpandedChecker] = useState<string | null>(null)
  const [verdictDialog, setVerdictDialog] = useState<Verdict | null>(null)
  const [verdictComment, setVerdictComment] = useState("")
  const [verdictLoading, setVerdictLoading] = useState(false)

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

  const submitVerdict = async () => {
    if (!verdictDialog) return
    setVerdictLoading(true)
    try {
      await onSetVerdict(verdictDialog, verdictComment.trim())
      setVerdictDialog(null)
      setVerdictComment("")
    } finally {
      setVerdictLoading(false)
    }
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>Карточка проверки #{submission.id}</h2>
        <p>Детализация чекеров, AI-анализ, вердикт и хронология</p>
      </header>

      <ScoreCard
        title={assignment?.title ?? submission.assignmentTitle ?? `Задание #${submission.assignmentId}`}
        candidate={submission.candidateFullName ?? `Кандидат #${submission.candidateId}`}
        score={submission.finalScore}
        status={submission.status}
      />

      {submission.finalScore !== null ? (
        <div className="score-progress">
          <span className="field-label">Итоговый прогресс</span>
          <ProgressBar value={submission.finalScore} />
        </div>
      ) : null}

      <div className="details-grid">
        <article className="card">
          <h3>Детализация проверок</h3>
          {results.length === 0 ? <p className="text-muted">Результаты ещё не готовы</p> : null}
          {results.map((result) => (
            <ResultRow
              key={result.checker}
              result={result}
              expanded={expandedChecker === result.checker}
              onToggle={() => setExpandedChecker(expandedChecker === result.checker ? null : result.checker)}
            />
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
                <Button onClick={() => setVerdictDialog("approved")}>Принять</Button>
                <Button variant="danger" onClick={() => setVerdictDialog("rejected")}>
                  Отклонить
                </Button>
              </>
            ) : null}
          </div>
          {submission.verdict !== "pending" ? (
            <p className="verdict-note">
              Вердикт: {VERDICT_LABELS[submission.verdict] ?? submission.verdict}
              {submission.verdictComment ? ` — ${submission.verdictComment}` : ""}
            </p>
          ) : null}
        </article>
      </div>

      <article className="card">
        <h3>Хронология событий</h3>
        <ul className="timeline">
          {timeline.map((item) => (
            <li key={`${item.event}-${item.timestamp}`}>
              <span>{item.label}</span>
              <span>{formatUtcToMsk(item.timestamp)}</span>
            </li>
          ))}
        </ul>
      </article>

      {verdictDialog ? (
        <div className="modal-overlay">
          <div className="modal verdict-modal">
            <h3>{verdictDialog === "approved" ? "Принять кандидата" : "Отклонить кандидата"}</h3>
            <label className="field">
              <span className="field-label">Комментарий</span>
              <textarea
                className="field-input"
                rows={4}
                value={verdictComment}
                onChange={(e) => setVerdictComment(e.target.value)}
                placeholder="Обоснование вердикта"
              />
            </label>
            <div className="auth-actions">
              <Button variant="secondary" onClick={() => setVerdictDialog(null)}>
                Отмена
              </Button>
              <Button variant={verdictDialog === "rejected" ? "danger" : "primary"} onClick={submitVerdict} loading={verdictLoading}>
                Сохранить вердикт
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  )
}
