type Props = {
  status: "pending" | "running" | "passed" | "failed" | "error" | "done"
}

export function StatusBadge({ status }: Props) {
  const normalized = status === "done" ? "passed" : status
  return <span className={`status-badge status-${normalized}`}>{status}</span>
}
