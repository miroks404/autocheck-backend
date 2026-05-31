/**
 * DashboardScreen — рабочее пространство эксперта: таблица проверок, поиск и фильтры.
 * Дата создания: 31-05-2026. Автор: Team 4.
 */
import { useMemo, useState } from "react"
import { DataTable } from "../components/ui/DataTable"
import { StatusBadge } from "../components/ui/StatusBadge"
import { FilterChip } from "../components/ui/FilterChip"
import { formatUtcToMsk } from "../shared/date"
import { STATUS_LABELS } from "../shared/labels"
import type { Assignment, Submission } from "../domain/models"
import { Button } from "../components/ui/Button"

type Props = {
  submissions: Submission[]
  assignments: Assignment[]
  canCreateAssignment: boolean
  onCreateAssignment: () => void
  onSelectSubmission: (submission: Submission) => void
}

export function DashboardScreen({
  submissions,
  assignments,
  canCreateAssignment,
  onCreateAssignment,
  onSelectSubmission,
}: Props) {
  const [query, setQuery] = useState("")
  const [assignmentFilter, setAssignmentFilter] = useState<number | "">("")
  const [statusFilters, setStatusFilters] = useState<Array<Submission["status"]>>([])
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [page, setPage] = useState(1)

  const filtered = useMemo(() => {
    return submissions.filter((item) => {
      const textTarget = `${item.candidateFullName ?? ""} ${item.candidateEmail ?? ""} ${item.id}`.toLowerCase()
      const matchesQuery = !query.trim() || textTarget.includes(query.trim().toLowerCase())
      const matchesAssignment = !assignmentFilter || item.assignmentId === assignmentFilter
      const matchesStatus = statusFilters.length === 0 || statusFilters.includes(item.status)

      const date = item.createdAt ? new Date(item.createdAt) : null
      const from = dateFrom ? new Date(dateFrom) : null
      const to = dateTo ? new Date(dateTo) : null
      const matchesDateFrom = !from || (date && date >= from)
      const matchesDateTo = !to || (date && date <= new Date(to.getTime() + 24 * 60 * 60 * 1000))

      return matchesQuery && matchesAssignment && matchesStatus && matchesDateFrom && matchesDateTo
    })
  }, [submissions, query, assignmentFilter, statusFilters, dateFrom, dateTo])

  const assignmentTitle = (id: number) =>
    submissions.find((s) => s.assignmentId === id)?.assignmentTitle ??
    assignments.find((a) => a.id === id)?.title ??
    `Задание #${id}`

  const toggleStatus = (status: Submission["status"]) => {
    setStatusFilters((prev) => (prev.includes(status) ? prev.filter((s) => s !== status) : [...prev, status]))
    setPage(1)
  }

  const clearFilters = () => {
    setQuery("")
    setAssignmentFilter("")
    setStatusFilters([])
    setDateFrom("")
    setDateTo("")
    setPage(1)
  }

  const activeChips: Array<{ key: string; label: string; onRemove: () => void }> = []
  if (query.trim()) activeChips.push({ key: "query", label: `Поиск: ${query.trim()}`, onRemove: () => setQuery("") })
  if (assignmentFilter) {
    activeChips.push({
      key: "assignment",
      label: `Задание: ${assignmentTitle(assignmentFilter)}`,
      onRemove: () => setAssignmentFilter(""),
    })
  }
  statusFilters.forEach((status) =>
    activeChips.push({
      key: `status-${status}`,
      label: `Статус: ${STATUS_LABELS[status]}`,
      onRemove: () => setStatusFilters((prev) => prev.filter((s) => s !== status)),
    }),
  )
  if (dateFrom) activeChips.push({ key: "from", label: `С: ${dateFrom}`, onRemove: () => setDateFrom("") })
  if (dateTo) activeChips.push({ key: "to", label: `По: ${dateTo}`, onRemove: () => setDateTo("") })

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>Дашборд эксперта</h2>
        <p>Таблица проверок, поиск и фильтры</p>
      </header>

      <div className="toolbar">
        <input
          className="field-input"
          placeholder="Поиск по ФИО кандидата"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setPage(1)
          }}
        />
        <select
          className="field-input"
          value={assignmentFilter}
          onChange={(e) => {
            setAssignmentFilter(e.target.value ? Number(e.target.value) : "")
            setPage(1)
          }}
        >
          <option value="">Все задания</option>
          {assignments.map((a) => (
            <option key={a.id} value={a.id}>
              {a.title}
            </option>
          ))}
        </select>
        <input className="field-input" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
        <input className="field-input" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
      </div>

      <div className="chip-row">
        {(["pending", "running", "done", "error"] as Array<Submission["status"]>).map((status) => (
          <button
            key={status}
            type="button"
            className={`chip ${statusFilters.includes(status) ? "chip-active" : ""}`}
            onClick={() => toggleStatus(status)}
          >
            {STATUS_LABELS[status]}
          </button>
        ))}
        <Button variant="secondary" onClick={clearFilters}>
          Сбросить все
        </Button>
        {canCreateAssignment ? (
          <Button onClick={onCreateAssignment}>Создать тестовое задание</Button>
        ) : null}
      </div>

      {activeChips.length > 0 ? (
        <div className="chip-row">
          {activeChips.map((chip) => (
            <FilterChip key={chip.key} label={chip.label} onRemove={chip.onRemove} />
          ))}
        </div>
      ) : null}

      <DataTable
        rows={filtered}
        page={page}
        onPageChange={setPage}
        onRowClick={onSelectSubmission}
        columns={[
          {
            key: "candidate",
            title: "Кандидат",
            sortable: true,
            sortValue: (row) => row.candidateFullName ?? `#${row.candidateId}`,
            render: (row) => row.candidateFullName ?? `#${row.candidateId}`,
          },
          {
            key: "assignment",
            title: "Задание",
            sortable: true,
            sortValue: (row) => assignmentTitle(row.assignmentId),
            render: (row) => assignmentTitle(row.assignmentId),
          },
          {
            key: "date",
            title: "Дата загрузки",
            sortable: true,
            sortValue: (row) => row.createdAt ?? "",
            render: (row) => formatUtcToMsk(row.createdAt),
          },
          {
            key: "status",
            title: "Статус",
            sortable: true,
            sortValue: (row) => row.status,
            render: (row) => <StatusBadge status={row.status} />,
          },
          {
            key: "score",
            title: "Итоговый балл",
            sortable: true,
            sortValue: (row) => row.finalScore ?? -1,
            render: (row) => (row.finalScore === null ? "—" : row.finalScore),
          },
        ]}
      />
    </section>
  )
}
