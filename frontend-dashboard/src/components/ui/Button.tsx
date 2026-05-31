type ButtonProps = {
  children: React.ReactNode
  variant?: "primary" | "secondary" | "danger"
  loading?: boolean
  disabled?: boolean
  onClick?: () => void
  type?: "button" | "submit"
}

export function Button({
  children,
  variant = "primary",
  loading = false,
  disabled = false,
  onClick,
  type = "button",
}: ButtonProps) {
  const classes = ["btn", `btn-${variant}`]
  if (loading) classes.push("btn-loading")

  return (
    <button type={type} className={classes.join(" ")} onClick={onClick} disabled={disabled || loading}>
      {loading ? "⏳" : null} {children}
    </button>
  )
}
