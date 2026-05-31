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
  technologies?: string[]
  candidateInstructions?: string
  checkerWeights: Record<string, number>
  status?: "draft" | "published"
  createdBy: number
  createdAt?: string | null
}

export type SubmissionStatus = "pending" | "running" | "done" | "error"

export type Verdict = "pending" | "approved" | "rejected"

export type Submission = {
  id: number
  assignmentId: number
  candidateId: number
  candidateFullName?: string
  candidateEmail?: string
  assignmentTitle?: string
  sourceType: string
  status: SubmissionStatus
  finalScore: number | null
  verdict: Verdict
  verdictComment?: string | null
  createdAt?: string | null
  updatedAt?: string | null
}

export type CheckResult = {
  checker: string
  status: "passed" | "failed" | "error"
  score: number
  message: string
  details?: Record<string, unknown> | null
  createdAt?: string | null
}

export type TimelineEvent = {
  event: string
  label: string
  timestamp?: string | null
  status?: string
  score?: number
  verdict?: string
  comment?: string | null
  finalScore?: number | null
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
