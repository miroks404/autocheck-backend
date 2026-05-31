import { useMemo, useState } from "react"

type Column<T> = {
  key: string
  title: string
  sortable?: boolean
  render: (row: T) => React.ReactNode
  sortValue?: (row: T) => string | number
}

type Props<T> = {
  columns: Array<Column<T>>
  rows: T[]
  page: number
  pageSize?: number
  onPageChange: (page: number) => void
  onRowClick?: (row: T) => void
}

export function DataTable<T extends { id: number | string }>({
  columns,
  rows,
  page,
  pageSize = 50,
  onPageChange,
  onRowClick,
}: Props<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc")

  const sortedRows = useMemo(() => {
    if (!sortKey) return rows
    const column = columns.find((col) => col.key === sortKey)
    if (!column?.sortValue) return rows
    return [...rows].sort((a, b) => {
      const left = column.sortValue!(a)
      const right = column.sortValue!(b)
      if (left < right) return sortDir === "asc" ? -1 : 1
      if (left > right) return sortDir === "asc" ? 1 : -1
      return 0
    })
  }, [rows, columns, sortKey, sortDir])

  const start = (page - 1) * pageSize
  const pageRows = sortedRows.slice(start, start + pageSize)
  const pages = Math.max(1, Math.ceil(sortedRows.length / pageSize))

  const toggleSort = (key: string, sortable?: boolean, sortValue?: (row: T) => string | number) => {
    if (!sortable || !sortValue) return
    if (sortKey === key) setSortDir((prev) => (prev === "asc" ? "desc" : "asc"))
    else {
      setSortKey(key)
      setSortDir("asc")
    }
    onPageChange(1)
  }

  return (
    <div className="table-wrap">
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key}>
                  {col.sortable ? (
                    <button type="button" className="sort-header" onClick={() => toggleSort(col.key, col.sortable, col.sortValue)}>
                      {col.title}
                      {sortKey === col.key ? (sortDir === "asc" ? " ↑" : " ↓") : ""}
                    </button>
                  ) : (
                    col.title
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row) => (
              <tr key={row.id} onClick={() => onRowClick?.(row)} className={onRowClick ? "row-clickable" : ""}>
                {columns.map((col) => (
                  <td key={col.key}>{col.render(row)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-footer">
        <button type="button" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          ← Назад
        </button>
        <span>
          Страница {page} / {pages}
        </span>
        <button type="button" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>
          Вперёд →
        </button>
      </div>
    </div>
  )
}
