import { useMe, useLogout } from '@/api/auth'
import { AuthPage } from '@/components/AuthPage'
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
    <div className="flex min-h-screen items-center justify-center">
      <div className="space-y-4 text-center">
        <h1 className="text-xl font-semibold">Welcome, {me.data.name}</h1>
        <p className="text-sm text-muted-foreground">{me.data.email}</p>
        <Button variant="outline" onClick={() => logout.mutate()}>
          Log out
        </Button>
      </div>
    </div>
  )
}
