import { useMemo, useState } from "react"
import { Button } from "../components/ui/Button"
import { Input } from "../components/ui/Input"

const defaultWeights = {
  static_analysis: 20,
  architecture: 20,
  build: 20,
  tests: 20,
  documentation: 10,
  git_practices: 10,
}

type Props = {
  open: boolean
  onClose: () => void
  onPublish: (payload: { title: string; description: string; checker_weights: Record<string, number> }) => Promise<void>
}

export function AssignmentCreateScreen({ open, onClose, onPublish }: Props) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [technologies, setTechnologies] = useState("")
  const [instructions, setInstructions] = useState("")
  const [weights, setWeights] = useState(defaultWeights)
  const [loading, setLoading] = useState(false)

  const sum = useMemo(() => Object.values(weights).reduce((acc, value) => acc + Number(value || 0), 0), [weights])
  const canPublish = title.trim().length > 2 && description.trim().length > 4 && sum === 100

  if (!open) return null

  const setWeight = (key: keyof typeof defaultWeights, value: string) => {
    const numeric = Math.max(0, Math.min(100, Number(value || 0)))
    setWeights((prev) => ({ ...prev, [key]: numeric }))
  }

  const publish = async () => {
    if (!canPublish) return
    setLoading(true)
    try {
      await onPublish({
        title: title.trim(),
        description: `${description}\n\n## Technologies\n${technologies}\n\n## Candidate instructions\n${instructions}`,
        checker_weights: weights,
      })
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
        <Input label="Технологии (теги через запятую)" value={technologies} onChange={setTechnologies} />
        <label className="field">
          <span className="field-label">Инструкции кандидату (markdown)</span>
          <textarea className="field-input" rows={3} value={instructions} onChange={(e) => setInstructions(e.target.value)} />
        </label>
        <div className="weight-grid">
          {(Object.keys(weights) as Array<keyof typeof defaultWeights>).map((key) => (
            <label key={key} className="field">
              <span className="field-label">{key}</span>
              <input
                className="field-input"
                type="number"
                min={0}
                max={100}
                value={weights[key]}
                onChange={(e) => setWeight(key, e.target.value)}
              />
            </label>
          ))}
        </div>
        <p>Сумма весов: {sum}%</p>
        <div className="auth-actions">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button onClick={publish} disabled={!canPublish} loading={loading}>
            Опубликовать
          </Button>
        </div>
      </div>
    </div>
  )
}
