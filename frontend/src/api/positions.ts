import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from './client'

export function usePositions() {
  return useQuery({
    queryKey: ['positions'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/positions')
      if (error) throw new Error('Failed to load positions')
      return data
    },
    refetchInterval: 30_000,
  })
}

export function usePortfolio() {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/portfolio')
      if (error) throw new Error('Failed to load portfolio')
      return data
    },
    refetchInterval: 30_000,
  })
}

export function useClosePosition() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await api.POST('/api/positions/{position_id}/close', {
        params: { path: { position_id: id } },
      })
      if (error) throw new Error('Failed to close position')
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['positions'] })
      void queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}
