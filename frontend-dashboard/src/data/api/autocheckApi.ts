import type { AiReview, Assignment, AuthUser, CheckResult, ReportStats, Submission, TimelineEvent, Verdict } from "../../domain/models"
import { httpRequest, httpRequestText } from "./httpClient"

type ApiEnvelope<T> = {
  data: T
  error: null | { code: string; message: string; details: unknown }
  meta: Record<string, unknown>
}

export const apiClient = {
  login(email: string, password: string) {
    return httpRequest<ApiEnvelope<{ accessToken: string; user: AuthUser }>>("POST", "/api/v1/auth/login", null, {
      email,
      password,
    })
  },
  register(payload: { full_name: string; email: string; password: string }) {
    return httpRequest<ApiEnvelope<unknown>>("POST", "/api/v1/auth/register", null, {
      ...payload,
      role: "candidate",
    })
  },
  profile(token: string) {
    return httpRequest<ApiEnvelope<AuthUser>>("GET", "/api/v1/auth/profile", token)
  },
  logout(token: string) {
    return httpRequest<ApiEnvelope<{ message: string }>>("POST", "/api/v1/auth/logout", token)
  },
  listAssignments(token: string) {
    return httpRequest<ApiEnvelope<{ items: Assignment[]; total: number }>>("GET", "/api/v1/assignments", token)
  },
  createAssignment(
    token: string,
    payload: {
      title: string
      description: string
      checker_weights: Record<string, number>
      technologies?: string[]
      candidate_instructions?: string
      status?: "draft" | "published"
    },
  ) {
    return httpRequest<ApiEnvelope<Assignment>>("POST", "/api/v1/assignments", token, payload)
  },
  createSubmission(token: string, data: FormData) {
    return httpRequest<ApiEnvelope<Submission>>("POST", "/api/v1/submissions", token, data, true)
  },
  listSubmissions(token: string) {
    return httpRequest<ApiEnvelope<{ items: Submission[]; total: number }>>("GET", "/api/v1/submissions", token)
  },
  getSubmission(token: string, id: number) {
    return httpRequest<ApiEnvelope<Submission>>("GET", `/api/v1/submissions/${id}`, token)
  },
  getSubmissionStatus(token: string, id: number) {
    return httpRequest<ApiEnvelope<{ submissionId: number; status: Submission["status"]; updatedAt: string }>>(
      "GET",
      `/api/v1/submissions/${id}/status`,
      token,
    )
  },
  getSubmissionResults(token: string, id: number) {
    return httpRequest<ApiEnvelope<{ items: CheckResult[]; total: number }>>("GET", `/api/v1/submissions/${id}/results`, token)
  },
  rerunSubmission(token: string, id: number) {
    return httpRequest<ApiEnvelope<Submission>>("POST", `/api/v1/submissions/${id}/rerun`, token)
  },
  setVerdict(token: string, id: number, verdict: Verdict, comment?: string | null) {
    return httpRequest<ApiEnvelope<Submission>>("PUT", `/api/v1/submissions/${id}/verdict`, token, {
      verdict,
      comment: comment ?? null,
    })
  },
  getTimeline(token: string, id: number) {
    return httpRequest<ApiEnvelope<{ items: TimelineEvent[]; total: number }>>(
      "GET",
      `/api/v1/submissions/${id}/timeline`,
      token,
    )
  },
  getReportHtml(token: string, id: number) {
    return httpRequestText("GET", `/api/v1/submissions/${id}/report?format=html`, token)
  },
  getReport(token: string, id: number) {
    return httpRequest<ApiEnvelope<Record<string, unknown>>>("GET", `/api/v1/submissions/${id}/report`, token)
  },
  getAiReview(token: string, id: number) {
    return httpRequest<ApiEnvelope<AiReview>>("GET", `/api/v1/submissions/${id}/ai-review`, token)
  },
  getStats(token: string) {
    return httpRequest<ApiEnvelope<ReportStats>>("GET", "/api/v1/reports/stats", token)
  },
}
