import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from './client'

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/auth/me')
      if (error) return null
      return data
    },
    staleTime: 60_000,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: { email: string; password: string }) => {
      const { data, error } = await api.POST('/api/auth/login', { body })
      if (error) throw new Error(detailOf(error) ?? 'Login failed')
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['me'], data)
    },
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: { email: string; name: string; password: string }) => {
      const { data, error } = await api.POST('/api/auth/register', { body })
      if (error) throw new Error(detailOf(error) ?? 'Registration failed')
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['me'], data)
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.POST('/api/auth/logout')
    },
    onSuccess: () => {
      queryClient.setQueryData(['me'], null)
    },
  })
}

// Backend error bodies are FastAPI's { detail: string | [...] }
function detailOf(error: unknown): string | null {
  if (typeof error !== 'object' || error === null || !('detail' in error)) return null
  const detail: unknown = error.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === 'object' && d !== null && 'msg' in d ? String(d.msg) : String(d)))
      .join(', ')
  }
  return null
}
