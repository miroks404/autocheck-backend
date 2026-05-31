import { useState } from "react"
import { STATUS_LABELS } from "../../shared/labels"

type Props = {
  status: "pending" | "running" | "passed" | "failed" | "error" | "done"
}

export function StatusBadge({ status }: Props) {
  const normalized = status === "done" ? "passed" : status
  const label = STATUS_LABELS[normalized] ?? status
  return <span className={`status-badge status-${normalized} ${status === "running" ? "status-running-anim" : ""}`}>{label}</span>
}
