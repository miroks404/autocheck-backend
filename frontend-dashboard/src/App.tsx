import { useEffect, useState } from "react"
import "./index.css"
import { APP_NAME } from "./core/config"
import { ApiError } from "./data/api/httpClient"
import {
  authorize,
  fetchAiReview,
  fetchAssignments,
  fetchProfile,
  fetchReport,
  fetchStats,
  fetchSubmissionDetails,
  fetchSubmissions,
  publishAssignment,
  rerunSubmission,
  sendSubmission,
  setSubmissionVerdict,
} from "./domain/useCases"
import type { AiReview, Submission, Verdict } from "./domain/models"
import { AppProvider, useAppContext } from "./state/AppContext"
import { AuthScreen } from "./screens/AuthScreen"
import { UploadScreen } from "./screens/UploadScreen"
import { DashboardScreen } from "./screens/DashboardScreen"
import { SubmissionDetailsScreen } from "./screens/SubmissionDetailsScreen"
import { StatsScreen } from "./screens/StatsScreen"
import { ToastStack } from "./components/ToastStack"
import { AssignmentCreateScreen } from "./screens/AssignmentCreateScreen"
import { apiClient } from "./data/api/autocheckApi"

function AppInner() {
  const { state, dispatch, addToast } = useAppContext()
  const [activeTab, setActiveTab] = useState<"upload" | "dashboard" | "details" | "stats">("upload")
  const [createAssignmentOpen, setCreateAssignmentOpen] = useState(false)
  const [aiReview, setAiReview] = useState<AiReview | null>(null)

  const loadCollections = async (token: string) => {
    dispatch({ type: "SET_LOADING", payload: true })
    try {
      const [assignments, submissions, stats] = await Promise.all([
        fetchAssignments(token),
        fetchSubmissions(token),
        fetchStats(token),
      ])
      dispatch({ type: "SET_ASSIGNMENTS", payload: assignments })
      dispatch({ type: "SET_SUBMISSIONS", payload: submissions })
      dispatch({ type: "SET_STATS", payload: stats })
    } finally {
      dispatch({ type: "SET_LOADING", payload: false })
    }
  }

  const onAuthLogin = async (email: string, password: string) => {
    const auth = await authorize(email, password)
    dispatch({ type: "SET_TOKEN", payload: auth.accessToken })
    const user = await fetchProfile(auth.accessToken)
    dispatch({ type: "SET_USER", payload: user })
    await loadCollections(auth.accessToken)
    addToast("success", "Успешный вход")
  }

  const handleApiError = (error: unknown) => {
    if (!(error instanceof ApiError)) {
      addToast("error", error instanceof Error ? error.message : "Неизвестная ошибка")
      return
    }
    if (error.status === 401) {
      dispatch({ type: "SET_TOKEN", payload: null })
      dispatch({ type: "SET_USER", payload: null })
      addToast("error", "Сессия истекла, войдите снова")
      return
    }
    if (error.status === 403) addToast("error", "Недостаточно прав")
    else if (error.status === 422) addToast("error", "Ошибка валидации данных")
    else if (error.status >= 500) addToast("error", "Серверная ошибка")
    else addToast("error", error.message)
  }

  const trackSubmission = async (token: string, submissionId: number) => {
    const streamUrl = `${new URL("/api/v1/submissions/" + submissionId + "/events", apiClientBase()).toString()}`
    try {
      const response = await fetch(streamUrl, {
        headers: { Authorization: `Bearer ${token}`, Accept: "text/event-stream" },
      })
      if (!response.ok) throw new Error("SSE unavailable")
      const reader = response.body?.getReader()
      if (!reader) throw new Error("No stream reader")
      const decoder = new TextDecoder()
      let done = false
      while (!done) {
        const result = await reader.read()
        done = result.done
        if (!result.value) continue
        const text = decoder.decode(result.value, { stream: true })
        if (text.includes("error")) addToast("error", "Проверка завершилась с ошибкой")
      }
    } catch {
      for (let i = 0; i < 75; i += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 2000))
        const status = await apiClient.getSubmissionStatus(token, submissionId)
        if (status.data.status === "done" || status.data.status === "error") break
      }
    }
  }

  const onSubmitUpload = async (payload: { assignmentId: number; gitUrl?: string; zipFile?: File }) => {
    if (!state.token) return
    try {
      dispatch({ type: "SET_LOADING", payload: true })
      const submission = await sendSubmission(state.token, payload)
      await trackSubmission(state.token, submission.id)
      const details = await fetchSubmissionDetails(state.token, submission.id)
      dispatch({ type: "SET_SELECTED_SUBMISSION", payload: details.submission })
      dispatch({ type: "SET_SELECTED_RESULTS", payload: details.results })
      await loadCollections(state.token)
      setActiveTab("details")
      addToast("success", "Решение отправлено на проверку")
    } catch (error) {
      handleApiError(error)
    } finally {
      dispatch({ type: "SET_LOADING", payload: false })
    }
  }

  const onOpenSubmission = async (submission: Submission) => {
    if (!state.token) return
    try {
      const details = await fetchSubmissionDetails(state.token, submission.id)
      dispatch({ type: "SET_SELECTED_SUBMISSION", payload: details.submission })
      dispatch({ type: "SET_SELECTED_RESULTS", payload: details.results })
      setAiReview(null)
      setActiveTab("details")
    } catch (error) {
      handleApiError(error)
    }
  }

  const onLoadAiReview = async () => {
    if (!state.token || !state.selectedSubmission) return
    try {
      const review = await fetchAiReview(state.token, state.selectedSubmission.id)
      setAiReview(review)
    } catch (error) {
      handleApiError(error)
    }
  }

  const onDownloadReport = async () => {
    if (!state.token || !state.selectedSubmission) return
    try {
      const report = await fetchReport(state.token, state.selectedSubmission.id)
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `submission-${state.selectedSubmission.id}-report.json`
      a.click()
      URL.revokeObjectURL(url)
      addToast("success", "Отчёт скачан")
    } catch (error) {
      handleApiError(error)
    }
  }

  const onSetVerdict = async (verdict: Verdict) => {
    if (!state.token || !state.selectedSubmission) return
    try {
      const updated = await setSubmissionVerdict(state.token, state.selectedSubmission.id, verdict)
      dispatch({ type: "SET_SELECTED_SUBMISSION", payload: updated })
      await loadCollections(state.token)
      addToast("success", "Вердикт сохранён")
    } catch (error) {
      handleApiError(error)
    }
  }

  const onPublishAssignment = async (payload: { title: string; description: string; checker_weights: Record<string, number> }) => {
    if (!state.token) return
    try {
      await publishAssignment(state.token, payload)
      await loadCollections(state.token)
      addToast("success", "Задание создано")
    } catch (error) {
      handleApiError(error)
    }
  }

  const onRerun = async () => {
    if (!state.token || !state.selectedSubmission) return
    try {
      await rerunSubmission(state.token, state.selectedSubmission.id)
      await trackSubmission(state.token, state.selectedSubmission.id)
      const details = await fetchSubmissionDetails(state.token, state.selectedSubmission.id)
      dispatch({ type: "SET_SELECTED_SUBMISSION", payload: details.submission })
      dispatch({ type: "SET_SELECTED_RESULTS", payload: details.results })
      await loadCollections(state.token)
      addToast("success", "Проверка перезапущена")
    } catch (error) {
      handleApiError(error)
    }
  }

  useEffect(() => {
    const bootstrap = async () => {
      if (!state.token) return
      try {
        const user = await fetchProfile(state.token)
        dispatch({ type: "SET_USER", payload: user })
        await loadCollections(state.token)
      } catch (error) {
        handleApiError(error)
      }
    }
    void bootstrap()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <main className="app">
      <header className="topbar">
        <h1>{APP_NAME}</h1>
        <nav className="tabs">
          <button onClick={() => setActiveTab("upload")} className={activeTab === "upload" ? "tab-active" : ""}>
            Загрузка
          </button>
          <button onClick={() => setActiveTab("dashboard")} className={activeTab === "dashboard" ? "tab-active" : ""}>
            Дашборд
          </button>
          <button onClick={() => setActiveTab("details")} className={activeTab === "details" ? "tab-active" : ""}>
            Карточка
          </button>
          <button onClick={() => setActiveTab("stats")} className={activeTab === "stats" ? "tab-active" : ""}>
            Статистика
          </button>
        </nav>
      </header>

      {!state.token || !state.user ? (
        <AuthScreen onLogin={onAuthLogin} addToast={addToast} />
      ) : (
        <>
          {activeTab === "upload" ? (
            <UploadScreen assignments={state.assignments} onSubmit={onSubmitUpload} />
          ) : null}
          {activeTab === "dashboard" ? (
            <DashboardScreen
              submissions={state.submissions}
              assignments={state.assignments}
              canCreateAssignment={state.user.role === "expert" || state.user.role === "admin"}
              onCreateAssignment={() => setCreateAssignmentOpen(true)}
              onSelectSubmission={onOpenSubmission}
            />
          ) : null}
          {activeTab === "details" ? (
            <SubmissionDetailsScreen
              submission={state.selectedSubmission}
              assignment={state.assignments.find((a) => a.id === state.selectedSubmission?.assignmentId) ?? null}
              results={state.selectedResults}
              aiReview={aiReview}
              onLoadAiReview={onLoadAiReview}
              onDownloadReport={onDownloadReport}
              onSetVerdict={onSetVerdict}
              canSetVerdict={state.user.role === "expert" || state.user.role === "admin"}
            />
          ) : null}
          {activeTab === "stats" ? <StatsScreen stats={state.stats} submissions={state.submissions} /> : null}
          <div className="floating-actions">{state.selectedSubmission ? <button onClick={onRerun}>Перезапустить текущую проверку</button> : null}</div>
        </>
      )}

      <AssignmentCreateScreen
        open={createAssignmentOpen}
        onClose={() => setCreateAssignmentOpen(false)}
        onPublish={onPublishAssignment}
      />
      {state.isLoading ? <div className="loading">Загрузка...</div> : null}
      <ToastStack />
    </main>
  )
}

function apiClientBase() {
  return import.meta.env.VITE_API_BASE_URL || "http://192.168.1.137:8000"
}

export default function App() {
  return (
    <AppProvider>
      <AppInner />
    </AppProvider>
  )
}
