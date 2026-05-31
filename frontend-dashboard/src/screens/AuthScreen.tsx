import { useState } from "react"
import { Button } from "../components/ui/Button"
import { Input } from "../components/ui/Input"
import { createCandidateAccount } from "../domain/useCases"

type Props = {
  onLogin: (email: string, password: string) => Promise<void>
  addToast: (type: "info" | "success" | "error", message: string) => void
}

export function AuthScreen({ onLogin, addToast }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login")
  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    setLoading(true)
    try {
      if (mode === "register") {
        if (!fullName.trim()) {
          addToast("error", "Укажите ФИО")
          return
        }
        await createCandidateAccount({ full_name: fullName.trim(), email: email.trim(), password })
        addToast("success", "Аккаунт создан, выполняю вход")
      }
      await onLogin(email.trim(), password)
    } catch (error) {
      addToast("error", error instanceof Error ? error.message : "Ошибка аутентификации")
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="auth-screen">
      <h2>{mode === "login" ? "Вход в систему" : "Регистрация кандидата"}</h2>
      <p>JWT-аутентификация. Для регистрации доступна только роль candidate.</p>
      {mode === "register" ? (
        <Input label="ФИО" value={fullName} onChange={setFullName} placeholder="Иван Иванов" />
      ) : null}
      <Input label="Email" value={email} onChange={setEmail} placeholder="you@example.com" type="email" />
      <Input label="Пароль" value={password} onChange={setPassword} placeholder="Минимум 6 символов" type="password" />
      <div className="auth-actions">
        <Button onClick={submit} loading={loading}>
          {mode === "login" ? "Войти" : "Создать аккаунт"}
        </Button>
        <Button variant="secondary" onClick={() => setMode(mode === "login" ? "register" : "login")} disabled={loading}>
          {mode === "login" ? "Нужна регистрация" : "Есть аккаунт"}
        </Button>
      </div>
    </section>
  )
}
