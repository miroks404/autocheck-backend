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
  const start = (page - 1) * pageSize
  const pageRows = rows.slice(start, start + pageSize)
  const pages = Math.max(1, Math.ceil(rows.length / pageSize))

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pageRows.map((row) => (
            <tr key={row.id} onClick={() => onRowClick?.(row)}>
              {columns.map((col) => (
                <td key={col.key}>{col.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-footer">
        <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          ← Назад
        </button>
        <span>
          Страница {page} / {pages}
        </span>
        <button disabled={page >= pages} onClick={() => onPageChange(page + 1)}>
          Вперёд →
        </button>
      </div>
    </div>
  )
}
