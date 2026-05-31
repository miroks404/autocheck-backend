/**
 * AssignmentCreateScreen — форма создания задания с чекерами, весами и валидацией суммы 100%.
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
import { useMemo, useState } from "react"
import { Button } from "../components/ui/Button"
import { Input } from "../components/ui/Input"
import { Checkbox } from "../components/ui/Checkbox"
import { checkerLabel } from "../shared/labels"

const CHECKER_KEYS = [
  "static_analysis",
  "architecture",
  "build",
  "tests",
  "documentation",
  "git_practices",
] as const

const DEFAULT_WEIGHTS: Record<(typeof CHECKER_KEYS)[number], number> = {
  static_analysis: 20,
  architecture: 20,
  build: 20,
  tests: 20,
  documentation: 10,
  git_practices: 10,
}

const TECH_OPTIONS = ["Android", "iOS", "Flutter", "React Native", "Kotlin", "Swift"]

type Props = {
  open: boolean
  onClose: () => void
  onPublish: (payload: {
    title: string
    description: string
    technologies: string[]
    candidate_instructions: string
    checker_weights: Record<string, number>
    status: "draft" | "published"
  }) => Promise<void>
}

export function AssignmentCreateScreen({ open, onClose, onPublish }: Props) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [technologies, setTechnologies] = useState<string[]>([])
  const [instructions, setInstructions] = useState("")
  const [activeCheckers, setActiveCheckers] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(CHECKER_KEYS.map((key) => [key, true])),
  )
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS)
  const [loading, setLoading] = useState(false)

  const activeKeys = CHECKER_KEYS.filter((key) => activeCheckers[key])
  const sum = useMemo(
    () => activeKeys.reduce((acc, key) => acc + Number(weights[key] || 0), 0),
    [activeKeys, weights],
  )
  const canSave = title.trim().length > 2 && description.trim().length > 4 && activeKeys.length > 0 && sum === 100

  if (!open) return null

  const toggleTech = (tech: string) => {
    setTechnologies((prev) => (prev.includes(tech) ? prev.filter((t) => t !== tech) : [...prev, tech]))
  }

  const toggleChecker = (key: (typeof CHECKER_KEYS)[number], enabled: boolean) => {
    setActiveCheckers((prev) => ({ ...prev, [key]: enabled }))
    if (!enabled) setWeights((prev) => ({ ...prev, [key]: 0 }))
  }

  const setWeight = (key: (typeof CHECKER_KEYS)[number], value: number) => {
    setWeights((prev) => ({ ...prev, [key]: Math.max(0, Math.min(100, value)) }))
  }

  const buildPayload = (status: "draft" | "published") => ({
    title: title.trim(),
    description: description.trim(),
    technologies,
    candidate_instructions: instructions.trim(),
    checker_weights: Object.fromEntries(activeKeys.map((key) => [key, weights[key]])),
    status,
  })

  const save = async (status: "draft" | "published") => {
    if (!canSave && status === "published") return
    setLoading(true)
    try {
      await onPublish(buildPayload(status))
      onClose()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Создание тестового задания</h2>
        <Input label="Название задания" value={title} onChange={setTitle} />
        <label className="field">
          <span className="field-label">Описание</span>
          <textarea className="field-input" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
        </label>

        <div className="field">
          <span className="field-label">Технологии</span>
          <div className="chip-row">
            {TECH_OPTIONS.map((tech) => (
              <button
                key={tech}
                type="button"
                className={`chip ${technologies.includes(tech) ? "chip-active" : ""}`}
                onClick={() => toggleTech(tech)}
              >
                {tech}
              </button>
            ))}
          </div>
        </div>

        <div className="checker-config">
          <span className="field-label">Активные чекеры и веса</span>
          {CHECKER_KEYS.map((key) => (
            <div key={key} className="checker-row">
              <Checkbox
                label={checkerLabel(key)}
                checked={activeCheckers[key]}
                onChange={(checked) => toggleChecker(key, checked)}
              />
              <input
                className="field-input weight-slider"
                type="range"
                min={0}
                max={100}
                step={5}
                value={weights[key]}
                disabled={!activeCheckers[key]}
                onChange={(e) => setWeight(key, Number(e.target.value))}
              />
              <span className="weight-value">{weights[key]}%</span>
            </div>
          ))}
        </div>

        <label className="field">
          <span className="field-label">Инструкции кандидату (markdown)</span>
          <textarea className="field-input" rows={3} value={instructions} onChange={(e) => setInstructions(e.target.value)} />
        </label>

        <p className={sum === 100 ? "weight-ok" : "weight-error"}>Сумма весов: {sum}% (должно быть 100%)</p>

        <div className="auth-actions">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button variant="secondary" onClick={() => save("draft")} disabled={title.trim().length <= 2} loading={loading}>
            Сохранить черновик
          </Button>
          <Button onClick={() => save("published")} disabled={!canSave} loading={loading}>
            Опубликовать
          </Button>
        </div>
      </div>
    </div>
  )
}
