import type { SubmissionStatus } from "../domain/models"

export const STATUS_LABELS: Record<SubmissionStatus | "passed" | "failed", string> = {
  pending: "Ожидание",
  running: "Проверяется",
  done: "Завершено",
  error: "Ошибка",
  passed: "Пройдено",
  failed: "Не пройдено",
}

export const CHECKER_LABELS: Record<string, string> = {
  static_analysis: "Статический анализ",
  architecture: "Архитектура",
  build: "Сборка",
  tests: "Тесты",
  documentation: "Документация",
  git_practices: "Git-практики",
}

export const VERDICT_LABELS: Record<string, string> = {
  pending: "Не вынесен",
  approved: "Принят",
  rejected: "Отклонён",
}

export function checkerLabel(key: string): string {
  return CHECKER_LABELS[key] ?? key
}
