import { useQuery } from '@tanstack/react-query'

import { api } from './client'

export function useCards() {
  return useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/cards')
      if (error) throw new Error('Failed to load cards')
      return data
    },
    staleTime: Infinity, // reference data never changes
  })
}
