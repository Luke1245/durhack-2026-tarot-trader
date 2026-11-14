import { useMutation } from '@tanstack/react-query'

import { api } from './client'

export function useCreateReading() {
  return useMutation({
    mutationFn: async (body: { question?: string } = {}) => {
      const { data, error } = await api.POST('/api/readings', { body })
      if (error) throw new Error('Failed to draw cards')
      return data
    },
  })
}
