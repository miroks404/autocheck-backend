import { apiClient } from "../data/api/autocheckApi"
import type { Assignment, Submission, TimelineEvent, Verdict } from "./models"

export async function authorize(email: string, password: string) {
  const response = await apiClient.login(email, password)
  return response.data
}

export async function createCandidateAccount(payload: { full_name: string; email: string; password: string }) {
  await apiClient.register(payload)
}

export async function fetchProfile(token: string) {
  const response = await apiClient.profile(token)
  return response.data
}

export async function fetchAssignments(token: string): Promise<Assignment[]> {
  const response = await apiClient.listAssignments(token)
  return response.data.items
}

export async function publishAssignment(
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
  const response = await apiClient.createAssignment(token, payload)
  return response.data
}

export async function sendSubmission(
  token: string,
  payload: {
    assignmentId: number
    gitUrl?: string
    zipFile?: File
    candidateFullName?: string
    candidateEmail?: string
  },
): Promise<Submission> {
  const formData = new FormData()
  formData.append("assignment_id", String(payload.assignmentId))
  if (payload.gitUrl) formData.append("git_url", payload.gitUrl)
  if (payload.zipFile) formData.append("zip_file", payload.zipFile)
  if (payload.candidateFullName) formData.append("candidate_full_name", payload.candidateFullName)
  if (payload.candidateEmail) formData.append("candidate_email", payload.candidateEmail)
  const response = await apiClient.createSubmission(token, formData)
  return response.data
}

export async function fetchSubmissions(token: string): Promise<Submission[]> {
  const response = await apiClient.listSubmissions(token)
  return response.data.items
}

export async function fetchSubmissionDetails(token: string, submissionId: number) {
  const [submission, results] = await Promise.all([
    apiClient.getSubmission(token, submissionId),
    apiClient.getSubmissionResults(token, submissionId),
  ])
  return { submission: submission.data, results: results.data.items }
}

export async function fetchTimeline(token: string, submissionId: number): Promise<TimelineEvent[]> {
  const response = await apiClient.getTimeline(token, submissionId)
  return response.data.items
}

export async function rerunSubmission(token: string, submissionId: number) {
  const response = await apiClient.rerunSubmission(token, submissionId)
  return response.data
}

export async function setSubmissionVerdict(
  token: string,
  submissionId: number,
  verdict: Verdict,
  comment?: string | null,
) {
  const response = await apiClient.setVerdict(token, submissionId, verdict, comment)
  return response.data
}

export async function fetchStats(token: string) {
  const response = await apiClient.getStats(token)
  return response.data
}

export async function fetchAiReview(token: string, submissionId: number) {
  const response = await apiClient.getAiReview(token, submissionId)
  return response.data
}

export async function fetchReport(token: string, submissionId: number) {
  const response = await apiClient.getReport(token, submissionId)
  return response.data
}

export async function fetchReportHtml(token: string, submissionId: number) {
  return apiClient.getReportHtml(token, submissionId)
}

export async function fetchSubmissionStatus(token: string, submissionId: number) {
  const response = await apiClient.getSubmissionStatus(token, submissionId)
  return response.data
}
