import { useState } from 'react'

import { useMe, useLogout } from '@/api/auth'
import { AppHeader, type AppPage } from '@/components/AppHeader'
import { AuthPage } from '@/components/AuthPage'
import { Dashboard } from '@/components/Dashboard'
import { HomePage } from '@/components/HomePage'
import { PortfolioPage } from '@/components/PortfolioPage'

export default function App() {
  const me = useMe()
  const logout = useLogout()
  const [page, setPage] = useState<AppPage>('home')

  if (me.isLoading) {
    return <div className="flex min-h-screen items-center justify-center text-muted-foreground">Loading…</div>
  }

  if (!me.data) {
    return <AuthPage />
  }

  function handleLogout() {
    setPage('home')
    logout.mutate()
  }

  return (
    <div className="min-h-screen bg-background">
      <AppHeader
        currentPage={page}
        userName={me.data.name}
        logoutPending={logout.isPending}
        onNavigate={setPage}
        onLogout={handleLogout}
      />
      {page === 'home' ? (
        <HomePage onNavigate={setPage} />
      ) : page === 'draw' ? (
        <main className="mx-auto max-w-5xl px-4">
          <Dashboard />
        </main>
      ) : (
        <PortfolioPage />
      )}
    </div>
  )
}
