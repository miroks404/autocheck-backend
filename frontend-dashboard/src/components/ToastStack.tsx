import { useAppContext } from "../state/AppContext"

export function ToastStack() {
  const { state } = useAppContext()
  return (
    <div className="toast-stack">
      {state.toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`}>
          {toast.message}
        </div>
      ))}
    </div>
  )
}
