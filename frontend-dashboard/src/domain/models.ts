export type UserRole = "candidate" | "expert" | "admin"

export type AuthUser = {
  id: number
  email: string
  fullName: string
  role: UserRole
}

export type Assignment = {
  id: number
  title: string
  description: string
  checkerWeights: Record<string, number>
  createdBy: number
  createdAt?: string | null
}

export type SubmissionStatus = "pending" | "running" | "done" | "error"

export type Verdict = "pending" | "approved" | "rejected"

export type Submission = {
  id: number
  assignmentId: number
  candidateId: number
  sourceType: string
  status: SubmissionStatus
  finalScore: number | null
  verdict: Verdict
  createdAt?: string | null
  updatedAt?: string | null
}

export type CheckResult = {
  checker: string
  status: "passed" | "failed" | "error"
  score: number
  message: string
  details?: Record<string, unknown> | null
}

export type ReportStats = {
  checksLast30Days: number
  avgScore: number
  passRatePct: number
  topCandidates: Array<{
    candidateId: number
    fullName: string
    bestScore: number
    attempts: number
  }>
}

export type AiReview = {
  available: boolean
  summary: string
  strengths: string[]
  improvements: string[]
}
