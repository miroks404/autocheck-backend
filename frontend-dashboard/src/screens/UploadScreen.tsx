/**
 * UploadScreen — сценарий загрузки решения экспертом (assignment + Git/ZIP + данные кандидата).
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
import { useMemo, useState } from "react"
import type { Assignment, UserRole } from "../domain/models"
import { Button } from "../components/ui/Button"
import { FileUpload } from "../components/ui/FileUpload"
import { Input } from "../components/ui/Input"

type Props = {
  assignments: Assignment[]
  currentUserEmail?: string
  currentUserRole?: UserRole
  onSubmit: (payload: {
    assignmentId: number
    gitUrl?: string
    zipFile?: File
    candidateFullName: string
    candidateEmail: string
  }) => Promise<void>
}

export function UploadScreen({ assignments, currentUserEmail, currentUserRole, onSubmit }: Props) {
  const [mode, setMode] = useState<"git" | "zip">("git")
  const [assignmentId, setAssignmentId] = useState<number | null>(assignments[0]?.id ?? null)
  const [gitUrl, setGitUrl] = useState("")
  const [zipFile, setZipFile] = useState<File | null>(null)
  const [candidateName, setCandidateName] = useState("")
  const [candidateEmail, setCandidateEmail] = useState("")
  const [loading, setLoading] = useState(false)

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(candidateEmail.trim())
  const emailNormalized = candidateEmail.trim().toLowerCase()
  const ownEmailConflict =
    (currentUserRole === "expert" || currentUserRole === "admin") &&
    currentUserEmail &&
    emailNormalized === currentUserEmail.trim().toLowerCase()
  const sourceValid =
    mode === "git" ? /^https:\/\/.+/i.test(gitUrl.trim()) : Boolean(zipFile)

  const canSubmit =
    Boolean(assignmentId) &&
    candidateName.trim().length > 2 &&
    emailValid &&
    !ownEmailConflict &&
    sourceValid

  const assignmentOptions = useMemo(() => assignments.map((a) => ({ id: a.id, title: a.title })), [assignments])

  const submit = async () => {
    if (!assignmentId || !canSubmit) return
    setLoading(true)
    try {
      await onSubmit({
        assignmentId,
        gitUrl: mode === "git" ? gitUrl.trim() : undefined,
        zipFile: mode === "zip" ? zipFile ?? undefined : undefined,
        candidateFullName: candidateName.trim(),
        candidateEmail: candidateEmail.trim(),
      })
      setGitUrl("")
      setZipFile(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>Загрузка задания</h2>
        <p>Выберите задание, загрузите решение и укажите данные кандидата</p>
        {currentUserRole === "expert" || currentUserRole === "admin" ? (
          <p className="text-caption">Email кандидата должен отличаться от вашего email эксперта.</p>
        ) : null}
      </header>

      <label className="field">
        <span className="field-label">Тестовое задание</span>
        <select
          className="field-input"
          value={assignmentId ?? ""}
          onChange={(e) => setAssignmentId(Number(e.target.value) || null)}
        >
          <option value="">Выберите задание</option>
          {assignmentOptions.map((item) => (
            <option key={item.id} value={item.id}>
              {item.title}
            </option>
          ))}
        </select>
      </label>

      <div className="mode-switch">
        <button type="button" className={`chip ${mode === "git" ? "chip-active" : ""}`} onClick={() => setMode("git")}>
          Git URL
        </button>
        <button type="button" className={`chip ${mode === "zip" ? "chip-active" : ""}`} onClick={() => setMode("zip")}>
          ZIP-файл
        </button>
      </div>

      {mode === "git" ? (
        <Input
          label="Git URL (https://...)"
          value={gitUrl}
          onChange={setGitUrl}
          placeholder="https://github.com/user/repo"
          error={gitUrl && !/^https:\/\/.+/i.test(gitUrl.trim()) ? "Укажите URL в формате https://..." : null}
        />
      ) : (
        <FileUpload file={zipFile} onFileChange={setZipFile} />
      )}

      <Input label="ФИО кандидата" value={candidateName} onChange={setCandidateName} placeholder="Иван Иванов" />
      <Input
        label="Email кандидата"
        value={candidateEmail}
        onChange={setCandidateEmail}
        placeholder="candidate@example.com"
        type="email"
        error={
          candidateEmail && !emailValid
            ? "Некорректный email"
            : ownEmailConflict
              ? "Укажите email кандидата, а не свой"
              : null
        }
      />

      <Button onClick={submit} disabled={!canSubmit} loading={loading}>
        Отправить на проверку
      </Button>
    </section>
  )
}
