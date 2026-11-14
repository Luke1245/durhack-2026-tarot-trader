import { useMe, useLogout } from '@/api/auth'
import { AuthPage } from '@/components/AuthPage'
import { Dashboard } from '@/components/Dashboard'
import { Button } from '@/components/ui/button'

export default function App() {
  const me = useMe()
  const logout = useLogout()

  if (me.isLoading) {
    return <div className="flex min-h-screen items-center justify-center text-muted-foreground">Loading…</div>
  }

  if (!me.data) {
    return <AuthPage />
  }

  return (
    <div className="mx-auto max-w-5xl px-4">
      <header className="flex items-center justify-between py-4">
        <span className="font-semibold">Tarot Trader</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{me.data.name}</span>
          <Button variant="outline" size="sm" onClick={() => logout.mutate()}>
            Log out
          </Button>
        </div>
      </header>
      <Dashboard />
    </div>
  )
}
