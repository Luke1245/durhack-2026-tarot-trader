import { useState, type FormEvent } from 'react'

import { useLogin, useRegister } from '@/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

type Mode = 'login' | 'register'

export function AuthPage() {
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const login = useLogin()
  const register = useRegister()
  const pending = login.isPending || register.isPending

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      if (mode === 'login') {
        await login.mutateAsync({ email, password })
      } else {
        await register.mutateAsync({ email, name, password })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4 rounded-xl border p-6">
        <h1 className="text-xl font-semibold">{mode === 'login' ? 'Log in' : 'Create account'}</h1>

        <label className="block space-y-1">
          <span className="text-sm">Email</span>
          <Input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />
        </label>

        {mode === 'register' && (
          <label className="block space-y-1">
            <span className="text-sm">Name</span>
            <Input
              required
              minLength={1}
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
          </label>
        )}

        <label className="block space-y-1">
          <span className="text-sm">Password</span>
          <Input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          />
        </label>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <Button type="submit" disabled={pending} className="w-full">
          {pending ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Sign up'}
        </Button>

        <button
          type="button"
          className="text-sm text-muted-foreground hover:text-foreground"
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login')
            setError(null)
          }}
        >
          {mode === 'login' ? 'No account? Create one' : 'Have an account? Log in'}
        </button>
      </form>
    </div>
  )
}
