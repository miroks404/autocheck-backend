import { createContext, useContext, useMemo, useReducer } from "react"
import type { Assignment, AuthUser, CheckResult, ReportStats, Submission } from "../domain/models"

type Toast = { id: number; type: "info" | "success" | "error"; message: string }

type AppState = {
  token: string | null
  user: AuthUser | null
  assignments: Assignment[]
  submissions: Submission[]
  selectedSubmission: Submission | null
  selectedResults: CheckResult[]
  stats: ReportStats | null
  isLoading: boolean
  toasts: Toast[]
}

type Action =
  | { type: "SET_TOKEN"; payload: string | null }
  | { type: "SET_USER"; payload: AuthUser | null }
  | { type: "SET_ASSIGNMENTS"; payload: Assignment[] }
  | { type: "SET_SUBMISSIONS"; payload: Submission[] }
  | { type: "SET_SELECTED_SUBMISSION"; payload: Submission | null }
  | { type: "SET_SELECTED_RESULTS"; payload: CheckResult[] }
  | { type: "SET_STATS"; payload: ReportStats | null }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "ADD_TOAST"; payload: Toast }
  | { type: "REMOVE_TOAST"; payload: number }

const initialState: AppState = {
  token: localStorage.getItem("ac_web_token"),
  user: null,
  assignments: [],
  submissions: [],
  selectedSubmission: null,
  selectedResults: [],
  stats: null,
  isLoading: false,
  toasts: [],
}

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "SET_TOKEN":
      if (action.payload) localStorage.setItem("ac_web_token", action.payload)
      else localStorage.removeItem("ac_web_token")
      return { ...state, token: action.payload }
    case "SET_USER":
      return { ...state, user: action.payload }
    case "SET_ASSIGNMENTS":
      return { ...state, assignments: action.payload }
    case "SET_SUBMISSIONS":
      return { ...state, submissions: action.payload }
    case "SET_SELECTED_SUBMISSION":
      return { ...state, selectedSubmission: action.payload }
    case "SET_SELECTED_RESULTS":
      return { ...state, selectedResults: action.payload }
    case "SET_STATS":
      return { ...state, stats: action.payload }
    case "SET_LOADING":
      return { ...state, isLoading: action.payload }
    case "ADD_TOAST":
      return { ...state, toasts: [action.payload, ...state.toasts].slice(0, 5) }
    case "REMOVE_TOAST":
      return { ...state, toasts: state.toasts.filter((t) => t.id !== action.payload) }
    default:
      return state
  }
}

const AppContext = createContext<{
  state: AppState
  dispatch: React.Dispatch<Action>
  addToast: (type: Toast["type"], message: string) => void
} | null>(null)

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  const addToast = (type: Toast["type"], message: string) => {
    const id = Date.now() + Math.floor(Math.random() * 1000)
    dispatch({ type: "ADD_TOAST", payload: { id, type, message } })
    window.setTimeout(() => dispatch({ type: "REMOVE_TOAST", payload: id }), 3600)
  }

  const value = useMemo(() => ({ state, dispatch, addToast }), [state])
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAppContext() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error("useAppContext must be used inside AppProvider")
  return ctx
}
