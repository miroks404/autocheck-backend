import { useEffect, useState } from "react"
import "./index.css"
import { API_BASE_URL, APP_NAME } from "./core/config"
import { ApiError } from "./data/api/httpClient"
import {
  authorize,
  fetchAiReview,
  fetchAssignments,
  fetchProfile,
  fetchReportHtml,
  fetchStats,
  fetchSubmissionDetails,
  fetchSubmissionStatus,
  fetchSubmissions,
  fetchTimeline,
  publishAssignment,
  rerunSubmission,
  sendSubmission,
  setSubmissionVerdict,
} from "./domain/useCases"
import type { AiReview, Submission, TimelineEvent, Verdict } from "./domain/models"
import { AppProvider, useAppContext } from "./state/AppContext"
import { AuthScreen } from "./screens/AuthScreen"
import { UploadScreen } from "./screens/UploadScreen"
import { DashboardScreen } from "./screens/DashboardScreen"
import { SubmissionDetailsScreen } from "./screens/SubmissionDetailsScreen"
import { StatsScreen } from "./screens/StatsScreen"
import { ToastStack } from "./components/ToastStack"
import { AssignmentCreateScreen } from "./screens/AssignmentCreateScreen"

const TOKEN_PRESETS: Record<string, string> = {
  default: "#4c7fff",
  emerald: "#00e5a0",
  amber: "#f59e0b",
}

function AppInner() {
  const { state, dispatch, addToast } = useAppContext()
  const [activeTab, setActiveTab] = useState<"upload" | "dashboard" | "details" | "stats">("upload")
  const [createAssignmentOpen, setCreateAssignmentOpen] = useState(false)
  const [aiReview, setAiReview] = useState<AiReview | null>(null)
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [tokenPreset, setTokenPreset] = useState("default")

  useEffect(() => {
    document.documentElement.style.setProperty("--primary", TOKEN_PRESETS[tokenPreset] ?? TOKEN_PRESETS.default)
  }, [tokenPreset])

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

  const refreshSubmissionInLists = async (token: string, submissionId: number) => {
    const [details, events, submissions] = await Promise.all([
      fetchSubmissionDetails(token, submissionId),
      fetchTimeline(token, submissionId),
      fetchSubmissions(token),
    ])
    dispatch({ type: "SET_SELECTED_SUBMISSION", payload: details.submission })
    dispatch({ type: "SET_SELECTED_RESULTS", payload: details.results })
    dispatch({ type: "SET_SUBMISSIONS", payload: submissions })
    setTimeline(events)
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
    else addToast("error", error.message)
  }

  const trackSubmission = async (token: string, submissionId: number) => {
    const streamUrl = `${API_BASE_URL}/api/v1/submissions/${submissionId}/events`
    const applyStatus = async () => {
      await refreshSubmissionInLists(token, submissionId)
    }

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
        await applyStatus()
        const text = decoder.decode(result.value, { stream: true })
        if (text.includes("done")) break
        if (text.includes("error")) {
          addToast("error", "Проверка завершилась с ошибкой")
          break
        }
      }
      await applyStatus()
    } catch {
      for (let i = 0; i < 75; i += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 2000))
        const statusPayload = await fetchSubmissionStatus(token, submissionId)
        await applyStatus()
        if (statusPayload.status === "done" || statusPayload.status === "error") break
      }
    }
  }

  const onSubmitUpload = async (payload: {
    assignmentId: number
    gitUrl?: string
    zipFile?: File
    candidateFullName: string
    candidateEmail: string
  }) => {
    if (!state.token) return
    try {
      dispatch({ type: "SET_LOADING", payload: true })
      const submission = await sendSubmission(state.token, payload)
      await trackSubmission(state.token, submission.id)
      const details = await fetchSubmissionDetails(state.token, submission.id)
      dispatch({ type: "SET_SELECTED_SUBMISSION", payload: details.submission })
      dispatch({ type: "SET_SELECTED_RESULTS", payload: details.results })
      setTimeline(await fetchTimeline(state.token, submission.id))
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
      setTimeline(await fetchTimeline(state.token, submission.id))
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
      const html = await fetchReportHtml(state.token, state.selectedSubmission.id)
      const blob = new Blob([html], { type: "text/html;charset=utf-8" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `submission-${state.selectedSubmission.id}-report.html`
      a.click()
      URL.revokeObjectURL(url)
      addToast("success", "Отчёт скачан")
    } catch (error) {
      handleApiError(error)
    }
  }

  const onSetVerdict = async (verdict: Verdict, comment: string) => {
    if (!state.token || !state.selectedSubmission) return
    try {
      const updated = await setSubmissionVerdict(state.token, state.selectedSubmission.id, verdict, comment)
      dispatch({ type: "SET_SELECTED_SUBMISSION", payload: updated })
      setTimeline(await fetchTimeline(state.token, updated.id))
      await loadCollections(state.token)
      addToast("success", "Вердикт сохранён")
    } catch (error) {
      handleApiError(error)
    }
  }

  const onPublishAssignment = async (payload: {
    title: string
    description: string
    technologies: string[]
    candidate_instructions: string
    checker_weights: Record<string, number>
    status: "draft" | "published"
  }) => {
    if (!state.token) return
    try {
      await publishAssignment(state.token, payload)
      await loadCollections(state.token)
      addToast("success", payload.status === "draft" ? "Черновик сохранён" : "Задание опубликовано")
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
      setTimeline(await fetchTimeline(state.token, state.selectedSubmission.id))
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
        <h1 className="text-h1">{APP_NAME}</h1>
        <nav className="tabs">
          <button type="button" onClick={() => setActiveTab("upload")} className={activeTab === "upload" ? "tab-active" : ""}>
            Загрузка
          </button>
          <button type="button" onClick={() => setActiveTab("dashboard")} className={activeTab === "dashboard" ? "tab-active" : ""}>
            Дашборд
          </button>
          <button type="button" onClick={() => setActiveTab("details")} className={activeTab === "details" ? "tab-active" : ""}>
            Карточка
          </button>
          <button type="button" onClick={() => setActiveTab("stats")} className={activeTab === "stats" ? "tab-active" : ""}>
            Статистика
          </button>
        </nav>
        <label className="token-demo">
          <span className="text-caption">Демо токена primary</span>
          <select value={tokenPreset} onChange={(e) => setTokenPreset(e.target.value)}>
            <option value="default">Синий</option>
            <option value="emerald">Изумрудный</option>
            <option value="amber">Янтарный</option>
          </select>
        </label>
      </header>

      {!state.token || !state.user ? (
        <AuthScreen onLogin={onAuthLogin} addToast={addToast} />
      ) : (
        <>
          {activeTab === "upload" ? (
            <UploadScreen
              assignments={state.assignments}
              currentUserEmail={state.user.email}
              currentUserRole={state.user.role}
              onSubmit={onSubmitUpload}
            />
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
              timeline={timeline}
              aiReview={aiReview}
              onLoadAiReview={onLoadAiReview}
              onDownloadReport={onDownloadReport}
              onSetVerdict={onSetVerdict}
              canSetVerdict={state.user.role === "expert" || state.user.role === "admin"}
            />
          ) : null}
          {activeTab === "stats" ? <StatsScreen stats={state.stats} submissions={state.submissions} /> : null}
          <div className="floating-actions">
            {state.selectedSubmission ? (
              <button type="button" onClick={onRerun}>
                Перезапустить текущую проверку
              </button>
            ) : null}
          </div>
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

export default function App() {
  return (
    <AppProvider>
      <AppInner />
    </AppProvider>
  )
}
